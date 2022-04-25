import rsgislib

def drop_rows_by_attribute(
    vec_file: str,
    vec_lyr: str,
    sub_col: str,
    sub_vals: list,
    out_vec_file: str,
    out_vec_lyr: str,
    out_format: str = "GPKG",
):
    """
    A function which subsets an input vector layer based on a list of values.

    :param vec_file: Input vector file.
    :param vec_lyr: Input vector layer
    :param sub_col: The column used to subset the layer.
    :param sub_vals: A list of values used to subset the layer. If using contains or
                     start then regular expressions supported by the re library can
                     be provided.
    :param out_vec_file: The output vector file
    :param out_vec_lyr: The output vector layer
    :param out_format: The output vector format.
    :param match_type: The type of match for the subset. Options: equals (default) -
                       the same value. contains - string is anywhere within attribute
                       value. start - string matches the start of the attribute value.

    """
    import geopandas

    base_gpdf = geopandas.read_file(vec_file, layer=vec_lyr)

    first = True
    for val in sub_vals:
        print(val)
        if first:
            out_gpdf = base_gpdf.drop(base_gpdf[base_gpdf[sub_col] == val].index)
            first = False
        else:
            out_gpdf = out_gpdf.drop(out_gpdf[out_gpdf[sub_col] == val].index)

    if out_gpdf.shape[0] > 0:
        if out_format == "GPKG":
            out_gpdf.to_file(out_vec_file, layer=out_vec_lyr, driver=out_format)
        else:
            out_gpdf.to_file(out_vec_file, driver=out_format)
    else:
        raise rsgislib.RSGISPyException("No output file as no features selected.")



