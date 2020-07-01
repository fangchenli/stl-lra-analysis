from pathlib import Path

import geopandas as gpd
import pandas as pd


def get_absolute_zip_path(relative_path) -> str:
    p = Path(relative_path)
    file_url = p.resolve().as_uri()
    return file_url.replace("file", "zip")


def get_lra_properties() -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    vacant = pd.read_csv("../data/raw/6-1-2020-Vacant-Lot-List.csv")
    vacant["Address"] = vacant["Address"].map(lambda x: x.upper())

    hpp = pd.read_csv("../data/raw/5-1-2020-HPP-List.csv")
    hpp["Address"] = hpp["Address"].map(lambda x: x.upper())

    improved = pd.read_csv("../data/raw/6-1-2020-Improved-Property-List-2.csv")
    improved["Address"] = improved["Address"].map(lambda x: x.upper())
    return vacant, hpp, improved


def get_parcel_and_shape() -> (pd.DataFrame, gpd.GeoDataFrame):
    parcel = pd.read_csv("../data/raw/par.csv", encoding="ISO-8859-1", low_memory=False)
    parcel.rename(lambda s: s.split(",")[0], axis="columns", inplace=True)

    shape_path = "../data/raw/prcl_shape.zip"
    shape = gpd.read_file(get_absolute_zip_path(shape_path))
    shape = shape.astype({"HANDLE": "int64"})
    shape["centroid"] = shape["geometry"].centroid
    # shape["centroid"] = shape["geometry"].centroid.to_crs("EPSG:4326")
    # shape = shape.to_crs("EPSG:2263")
    return parcel, shape
