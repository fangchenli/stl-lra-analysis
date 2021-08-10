from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile

import pandas as pd
import requests
from bs4 import BeautifulSoup
from opendbf.dbf import dbf_to_csv

from src.utils import raw_path


def get_property_value(handle: int):
    url = "https://www.stlouis-mo.gov/government/departments/sldc/real-estate/lra-owned-property-search.cfm"
    param = {"HANDLE": handle}
    res = requests.get(url, params=param)
    soup = BeautifulSoup(res.content, "html.parser")
    tds = soup.find_all("td")
    for td in tds:
        tag_contents = td.contents
        if len(tag_contents) == 3:
            if "$" in tag_contents[0]:
                value_str = (
                    tag_contents[0].strip().replace("$", "", 1).replace(",", "", 1)
                )
                return (
                    float(value_str) if value_str.replace(".", "", 1).isdigit() else 0
                )


def download_lra_property_data(data_dir: Path):
    url = "https://www.stlouis-mo.gov/government/departments/sldc/real-estate/lra-owned-property-full-list.cfm"

    o = urlparse(url)
    base_url = url.replace(o.path, "")

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.endswith(".xlsx"):
            data_path = urljoin(base_url, href)
            base_name = Path(data_path).name
            file_path = Path(data_dir, base_name)
            csv_path = str(file_path).replace("xlsx", "csv")
            df = pd.read_excel(data_path)
            df.to_csv(csv_path, index=False)


def download_parcel_data(data_dir: Path):
    """
    Download parcels data from stl-lra website. The data is converted from dbf to cvs via opendbf.
    :param data_dir: output directory
    """
    url = "https://www.stlouis-mo.gov/data/upload/data-files/par.zip"
    res = requests.get(url)
    with ZipFile(BytesIO(res.content)) as zipfile:
        zipfile.extractall(data_dir)
    dbf_name = Path(url).name.replace("zip", "dbf")
    dbf_path = Path(data_dir, dbf_name)
    dbf_to_csv(str(dbf_path))
    dbf_path.unlink()


def download_parcel_shape(data_dir: Path):
    url = "https://www.stlouis-mo.gov/data/upload/data-files/prcl_shape.zip"
    base_name = Path(url).name
    save_dir = Path(data_dir, base_name)
    res = requests.get(url)
    with save_dir.open("wb") as file:
        file.write(res.content)


if __name__ == "__main__":
    download_lra_property_data(raw_path)
    download_parcel_data(raw_path)
    download_parcel_shape(raw_path)
