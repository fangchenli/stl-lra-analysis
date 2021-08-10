from pathlib import Path

import geopandas as gpd
import pandas as pd


root_path = Path(__file__).parent.parent
data_path = Path(root_path, "data")
raw_path = Path(data_path, "raw")
processed_path = Path(data_path, "processed")

if not data_path.exists():
    data_path.mkdir()

if not raw_path.exists():
    raw_path.mkdir()

if not processed_path.exists():
    raw_path.mkdir()


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


if __name__ == "__main__":
    vacant, improved = get_lra_properties()
    print(vacant.info())
    print(improved.info())
