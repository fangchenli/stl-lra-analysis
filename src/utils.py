from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon


def get_absolute_zip_path(relative_path) -> str:
    p = Path(relative_path)
    file_url = p.resolve().as_uri()
    return file_url.replace("file", "zip")


def get_lra_properties() -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    vacant = pd.read_csv("../data/raw/8-3-20-Vacant-Lot-List.csv")
    vacant["Address"] = vacant["Address"].map(lambda x: x.upper())

    hpp = pd.read_csv("../data/raw/8-3-20-HPP-Eligible-List.csv")
    hpp["Address"] = hpp["Address"].map(lambda x: x.upper())

    improved = pd.read_csv("../data/raw/8-3-20-Improved-Property-List.csv")
    improved["Address"] = improved["Address"].map(lambda x: x.upper())
    return vacant, hpp, improved


def get_parcel_and_shape() -> (pd.DataFrame, gpd.GeoDataFrame):
    parcel = pd.read_csv("../data/raw/par.csv", encoding="ISO-8859-1", low_memory=False)
    parcel.rename(lambda s: s.split(",")[0], axis="columns", inplace=True)

    shape_path = "../data/raw/prcl_shape.zip"
    shape = gpd.read_file(get_absolute_zip_path(shape_path))
    shape = shape.astype({"HANDLE": "int64"})

    # calculate centroid and convert all geometry to lat lon coordinate
    # shape["centroid"] = shape["geometry"].centroid
    # shape["centroid"] = shape["geometry"].centroid.to_crs("EPSG:4326")
    # shape = shape.to_crs("EPSG:4326")
    return parcel, shape


def crs_to_pixel_coordinate(shape: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

    # get the bounds for the whole shape
    min_x, _, _, max_y = shape["geometry"].total_bounds

    # transform it to zero base
    shape["geometry"] = shape["geometry"].translate(-min_x, -max_y)

    # get the exterior coordinates for the Polygons/MultiPolygons
    shape["coordinate"] = shape["geometry"].map(
        lambda x: list(x.exterior.coords)
        if isinstance(x, Polygon)
        else [list(e.exterior.coords) for e in x]
    )

    # negate the y-axis so it fits the canvas coordinate and expend the list of list for MultiPolygon
    shape["coordinate"] = shape["coordinate"].map(
        lambda x: [(pair[0], -pair[1]) for pair in x]
        if isinstance(x[0], tuple)
        else [(pair[0], -pair[1]) for e in x for pair in e]
    )

    # flatten the list of tuple to 1-d list of [x1, y1, x2, y2, x3, y3......]
    shape["coordinate"] = shape["coordinate"].map(
        lambda x: [coord for pair in x for coord in pair]
    )

    return shape
