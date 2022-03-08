"""
This module provides tools for the project.
"""
import geopandas as gp
from shapely.geometry import Point, Polygon


def in_square(
    square: tuple[float, float, float, float], point: tuple[float, float]
) -> bool:
    """
    Check if the point (x,y) is in the square (west, south, east, north)
    """
    west, south, east, north = square
    x, y = point
    return (west <= x and x <= east) and (south <= y and y <= north)


def raster_id_from_coordinates(
    coord: tuple[float, float],
    rasters_data: gp.GeoDataFrame,
    square_label: str,
    id_label: str,
) -> int:
    """
    Returns the id of the raster where the coord lies.
    """
    l = rasters_data.shape[0]
    i = 0
    while i < l:
        b = in_square(rasters_data.loc[i, square_label].bounds, coord)
        if b is True:
            id = rasters_data.loc[i, id_label]
            break
        i += 1
    return id


def rasters_of_bbox(
    bbox: tuple[float, float, float, float],
    data_rasters,
    square_label,
    id_label,
):
    """
    Given a bounding box, returns the rasters containing the bbox,
    in the form of a dictionnary.
    """
    data = gp.read_file(data_rasters)
    west, south, east, north = bbox
    id_min = raster_id_from_coordinates(
        (west, south), data, square_label, id_label
    )
    id_max = raster_id_from_coordinates(
        (east, north), data, square_label, id_label
    )
    if id_min == id_max:
        return {"all": id_min}
    else:
        id_top_left = raster_id_from_coordinates((west, north))
        if id_top_left == id_min:
            return {"left": id_min, "right": id_max}
        else:
            id_bottom_right = raster_id_from_coordinates((east, south))
            return {
                "top left": id_top_left,
                "bottom left": id_min,
                "bottom right": id_bottom_right,
                "top right": id_max,
            }


def bbox_enlarged(
    bbox: tuple[float, float, float, float], frac: float = 0.5
) -> tuple[float, float, float, float]:
    """
    Returns an enlarged bbox, according to the factor frac.
    """
    west, south, east, north = bbox
    delta_x = (east - west) * frac
    delta_y = (north - south) * frac
    return (west - delta_x, south - delta_y, east + delta_x, north + delta_y)


def bbox_enlarged_with_max_bounds(
    bbox: tuple[float, float, float, float],
    bbox_max: tuple[float, float, float, float],
    frac: float = 0.5,
) -> tuple[float, float, float, float]:
    """
    Returns an enlarged bbox, according to the factor frac, taking into account
    an explicit maximal bbox.
    """
    west, south, east, north = bbox_enlarged(bbox, frac=frac)
    West, South, East, North = bbox_max
    return (
        max(west, West),
        max(south, South),
        min(east, East),
        min(north, North),
    )


def square_envelope(bbox):
    xmin, ymin, xmax, ymax = bbox
    delta_x = (xmax - xmin) / 2
    delta_y = (ymax - ymin) / 2
    if delta_x > delta_y:
        y_center = (ymax + ymin) / 2
        return xmin, y_center - delta_x, xmax, y_center + delta_x
    elif delta_x < delta_y:
        x_center = (xmax + xmin) / 2
        return x_center - delta_y, ymin, x_center + delta_y, ymax
    else:
        return bbox
