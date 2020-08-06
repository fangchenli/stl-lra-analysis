from io import BytesIO
from os import mkdir, path, remove
from pathlib import Path
from subprocess import run
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile

import pandas as pd
import requests
from bs4 import BeautifulSoup


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


def download_lra_property_data(data_dir: str):
    url = "https://www.stlouis-mo.gov/government/departments/sldc/real-estate/lra-owned-property-full-list.cfm"

    o = urlparse(url)
    base_url = url.replace(o.path, "")

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    # find all "a" tags with href
    a_tags = soup.find_all("a", href=True)

    # download xlsx files and store to csv format
    for a_tag in a_tags:
        href = a_tag["href"]
        if href.endswith(".xlsx"):
            data_path = urljoin(base_url, href)
            base_name = path.basename(data_path)
            file_path = path.join(data_dir, base_name)
            csv_path = file_path.replace("xlsx", "csv")
            df = pd.read_excel(data_path)
            df.to_csv(csv_path, index=False)


def download_parcel_data(data_dir: str):
    """
    Download parcels data from stl website. The data is converted from dbf to cvs via LibreOffice.
    :param data_dir: output directory
    """
    url = "https://www.stlouis-mo.gov/data/upload/data-files/par.zip"
    res = requests.get(url)
    with ZipFile(BytesIO(res.content)) as zipfile:
        zipfile.extractall(data_dir)
    dbf_name = path.basename(url).replace("zip", "dbf")
    dbf_path = path.join(data_dir, dbf_name)
    run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "csv",
            "--outdir",
            data_dir,
            dbf_path,
        ]
    )
    remove(dbf_path)


def download_parcel_shape(data_dir: str):
    url = "https://www.stlouis-mo.gov/data/upload/data-files/prcl_shape.zip"
    base_name = path.basename(url)
    save_dir = path.join(data_dir, base_name)
    res = requests.get(url)
    with open(save_dir, "wb") as file:
        file.write(res.content)


if __name__ == "__main__":
    data_dir_path = Path("data", "raw")

    # create data directory if not exist
    if not path.exists(data_dir_path):
        mkdir(data_dir_path)

    download_lra_property_data(data_dir_path)
    download_parcel_data(data_dir_path)
    download_parcel_shape(data_dir_path)
