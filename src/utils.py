from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

root_path = Path(__file__).parent.parent
data_path = Path(root_path, "data")
raw_path = Path(data_path, "raw")


def get_absolute_zip_path(relative_path) -> str:
    p = Path(relative_path)
    file_url = p.resolve().as_uri()
    return file_url.replace("file", "zip")


def get_lra_properties() -> (pd.DataFrame, pd.DataFrame):
    data_dict = {}
    for path in raw_path.glob("*.csv"):
        file_name = path.name
        tokens = file_name.split("-")
        if len(tokens) > 1:
            _, _, _, name, _, _ = tokens
            df = pd.read_csv(path)
            df["Address"] = df["Address"].map(lambda x: x.upper())
            data_dict[name.lower()] = df
    return data_dict["vacant"], data_dict["improved"]


def get_parcel_and_shape() -> (pd.DataFrame, gpd.GeoDataFrame):
    parcel_path = Path(raw_path, "par.csv")
    parcel = pd.read_csv(parcel_path, encoding="ISO-8859-1", low_memory=False)
    parcel.rename(lambda s: s.split(",")[0], axis="columns", inplace=True)

    shape_path = Path(raw_path, "prcl_shape.zip")
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


if __name__ == "__main__":
    vacant, improved = get_lra_properties()
    print(vacant.info())
    print(improved.info())
