from typing import Union, Dict, List
import numpy


def limit_range_np_arr(
    arr_data: numpy.array,
    min_thres: float = 0,
    min_out_val: float = 0,
    max_thres: float = 1,
    max_out_val: float = 1,
) -> numpy.array:
    """
    A function which can be used to limit the range of the numpy array.
    For example, to mask values less than 0 to 0 and values greater than
    1 to 1.

    :param arr_data: input numpy array.
    :param min_thres: the threshold for the minimum value.
    :param min_out_val: the value assigned to values below the min_thres
    :param max_thres: the threshold for the maximum value.
    :param max_out_val: the value assigned to the values above the max_thres
    :return: numpy array with output values.

    """
    arr_data_out = arr_data.copy()
    arr_data_out[arr_data < min_thres] = min_out_val
    arr_data_out[arr_data > max_thres] = max_out_val
    return arr_data_out


def manual_stretch_np_arr(
    arr_data: numpy.array,
    min_max_vals: Union[Dict, List[Dict]],
    no_data_val: float = None,
    out_off: float = 0,
    out_gain: float = 1,
    out_int_type=False,
    min_out_val: float = 0,
    max_out_val: float = 1,
) -> numpy.array:
    """
    A function which performs a linear stretch using the min-max values provided
    on a per band basis for a numpy array representing an image dataset. This
    function is useful in combination with get_gdal_raster_mpl_imshow for
    displaying raster data from an input image as a plot. By default this function
    returns values in a range 0 - 1 but if you prefer 0 - 255 then set the out_gain
    to 255 and the out_int_type to be True to get an 8bit unsigned integer value.

    :param arr_data: The numpy array as either [n,m,b] or [n,m] where n and m are
                     the number of image pixels in the x and y axis' and b is the
                     number of image bands.
    :param min_max_vals: either a list of dicts each with a 'min' and 'max' key
                         specifying the min and max value for the stretch of each
                         band. Or, if just a single band then provide a single
                         dict rather than a list. The number items in the list
                         must equal the number of dimensions within the arr_data.
    :param no_data_val: the no data value for the input data. If there isn't a no
                        data value then leave as None (default)
    :param out_off: Output offset value (value * gain) + offset. Default: 0
    :param out_gain: Output gain value (value * gain) + offset. Default: 1
    :param out_int_type: False (default) and the output type will be float and
                         True and the output type with be integers.
    :param min_out_val: Minimum output value within the output array (default: 0)
    :param max_out_val: Maximum output value within the output array (default: 1)
    :return: A number array with the rescaled values but same dimensions as the
             input numpy array.

    .. code:: python

        img_sub_bbox = [554756, 577168, 9903924, 9944315]
        input_img = "sen2_img_strch.kea"

        img_data_arr, coords_bbox = get_gdal_raster_mpl_imshow(input_img,
                                                               bands=[8,9,3],
                                                               bbox=img_sub_bbox)

        min_max_vals = list()
        min_max_vals.append({'min':10, 'max':400})
        min_max_vals.append({'min':22, 'max':300})
        min_max_vals.append({'min':1, 'max':120})

        img_data_arr = manual_stretch_np_arr(img_data_arr,
                                             min_max_vals,
                                             no_data_val=0.0)


        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        im = ax.imshow(img_data_arr, extent=coords_bbox)
        plt.show()

    """
    arr_shp = arr_data.shape

    if no_data_val is not None:
        arr_data_out = arr_data.astype(float)
        arr_data_out[arr_data == no_data_val] = numpy.nan
    else:
        arr_data_out = arr_data.copy()

    if len(arr_shp) == 2:
        if type(min_max_vals) is not dict:
            raise rsgislib.RSGISPyException(
                "Just 1 dimension within arr_data and therefore "
                "min_max_vals variable must be a dict."
            )

        if ("min" not in min_max_vals) or ("max" not in min_max_vals):
            raise rsgislib.RSGISPyException(
                "min and max keys must be provided within the dict"
            )

        min_val = min_max_vals["min"]
        max_val = min_max_vals["max"]
        range_val = max_val - min_val

        arr_data_out = (((arr_data_out - min_val) / range_val) * out_gain) + out_off
    else:
        if type(min_max_vals) is not list:
            raise rsgislib.RSGISPyException(
                "arr_data has more than 1 dimension and therefore "
                "min_max_vals variable must be a list."
            )

        n_bands = arr_shp[2]

        if n_bands != len(min_max_vals):
            raise rsgislib.RSGISPyException(
                "length of min_max_vals must be the same as the number "
                "of bands in arr_data."
            )

        for n in range(n_bands):
            if ("min" not in min_max_vals[n]) or ("max" not in min_max_vals[n]):
                raise rsgislib.RSGISPyException(
                    "min and max keys must be provided within the dict"
                )

            min_val = min_max_vals[n]["min"]
            max_val = min_max_vals[n]["max"]
            range_val = max_val - min_val

            arr_data_out[..., n] = (
                ((arr_data_out[..., n] - min_val) / range_val) * out_gain
            ) + out_off

    arr_data_out = limit_range_np_arr(
        arr_data_out,
        min_thres=min_out_val,
        min_out_val=min_out_val,
        max_thres=max_out_val,
        max_out_val=max_out_val,
    )

    if out_int_type:
        arr_data_out = arr_data_out.astype(int)

    return arr_data_out
