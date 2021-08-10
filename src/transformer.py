from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.downloader import get_property_value
from src.utils import processed_path


def construct_geojson(
    parcel: pd.DataFrame, shape: gpd.GeoDataFrame, data: pd.DataFrame
):

    # filter out parcel and shape for vacant lot
    vacant_parcel = parcel[parcel["SITEADDR"].isin(data["Address"])]
    vacant_shape = shape[shape["HANDLE"].isin(vacant_parcel["HANDLE"])]

    vacant_shape = vacant_shape.to_crs("EPSG:4326")

    vacant_join = vacant_shape.join(vacant_parcel.set_index("HANDLE"), on="HANDLE")
    vacant_join = vacant_join.rename(columns={"SITEADDR": "Address"})
    vacant_join = vacant_join.join(data.set_index("Address"), on="Address")
    vacant_join = vacant_join[["geometry", "HANDLE", "Address", "LotSF", "Front"]]

    vacant_join = vacant_join.join(vacant_shape, lsuffix="_caller", rsuffix="_other")
    vacant_join = vacant_join.drop(columns=["geometry_other", "HANDLE_other"])
    vacant_join = vacant_join.rename(
        columns={"geometry_caller": "geometry", "HANDLE_caller": "HANDLE"}
    )

    vacant_join["Value"] = vacant_join["HANDLE"].map(lambda x: get_property_value(x))
    vacant_join["ValuePerSF"] = vacant_join["Value"] / vacant_join["LotSF"]

    file_path = Path(processed_path, "vacant.geojson")
    vacant_join.to_file(file_path, driver="GeoJSON")
