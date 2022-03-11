import numpy

import osgeo.gdal as gdal

import rsgislib


def get_img_pxl_coords(
    input_img: str, x_coords: numpy.array, y_coords: numpy.array
) -> (numpy.array, numpy.array):
    """
    A function which calculates the image pixel coordinates for a set of
    spatial coordinates for the input_img. Note, the input coordinates
    must be within the input image extent.

    :param input_img: Input image file path. This image defines the spatial coordinate
                      system and extent for the conversion of the input coordinates.
    :param x_coords: Numpy array of x coordinates
    :param y_coords: Numpy array of y coordinates
    :return: x_pxl_coords, y_pxl_coords. A pair of numpy arrays with the image
             pixel coordinates for the input spatial coordinates.

    """
    img_ds = gdal.Open(input_img, gdal.GA_ReadOnly)
    if img_ds is None:
        raise rsgislib.RSGISPyException(
            "Could not open raster image: {}".format(input_img)
        )

    x_size = img_ds.RasterXSize
    y_size = img_ds.RasterYSize

    geo_transform = img_ds.GetGeoTransform()
    tl_x = geo_transform[0]
    tl_y = geo_transform[3]

    x_res = abs(geo_transform[1])
    y_res = abs(geo_transform[5])

    br_x = tl_x + (x_res * x_size)
    br_y = tl_y - (y_res * y_size)

    if numpy.any((x_coords < tl_x) | (x_coords > br_x)):
        raise rsgislib.RSGISPyException(
            "Coordinates outside the image extent were passed (x-axis)"
        )
    if numpy.any((y_coords < br_y) | (y_coords > tl_y)):
        raise rsgislib.RSGISPyException(
            "Coordinates outside the image extent were passed (y-axis)"
        )

    x_pxl_coords = numpy.floor(((x_coords - tl_x) / x_res) + 0.5).astype(int)
    y_pxl_coords = numpy.floor(((tl_y - y_coords) / y_res) + 0.5).astype(int)

    return x_pxl_coords, y_pxl_coords

def get_img_pxl_column(
    input_img: str, x_pxl_coord: int, y_pxl_coord: int
) -> numpy.array:
    """
    Function which gets pixel band values for a single pixel within an image.
    The coordinate space is image pixels, i.e., (0 - xSize) and (0 - ySize).

    :param input_img: The input image name and path
    :param x_pxl_coord: An image X coordinate (in the image pixel coordinates)
    :param y_pxl_coord: An image Y coordinate (in the image pixel coordinates)
    :return: An array of image pixel values (length = the number of image bands).

    """
    import struct

    image_ds = gdal.Open(input_img, gdal.GA_ReadOnly)
    if image_ds is None:
        raise rsgislib.RSGISPyException(
            "Could not open the input image file: '{}'".format(input_img)
        )
    n_bands = image_ds.RasterCount
    out_pxl_vals_byte = image_ds.ReadRaster(
        xoff=int(x_pxl_coord),
        yoff=int(y_pxl_coord),
        xsize=1,
        ysize=1,
        band_list=None,
        buf_type=gdal.GDT_Float32,
    )
    out_pxl_vals = struct.unpack("f" * n_bands, out_pxl_vals_byte)
    image_ds = None
    return numpy.array(out_pxl_vals)