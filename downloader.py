from os import mkdir, path, remove
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile
from io import BytesIO
from subprocess import run

import pandas as pd
import requests
from bs4 import BeautifulSoup


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

            # get the file
            r = requests.get(data_path, allow_redirects=True)

            base_name = path.basename(data_path)
            file_path = path.join(data_dir, base_name)

            # write the content of the request to local dir
            with open(file_path, "wb") as f:
                f.write(r.content)

            df = pd.read_excel(data_path)
            csv_path = file_path.replace("xlsx", "csv")
            df.to_csv(csv_path, index=False)
            remove(file_path)


def download_parcel_data(data_dir: str):
    url = 'https://www.stlouis-mo.gov/data/upload/data-files/par.zip'
    res = requests.get(url)
    with ZipFile(BytesIO(res.content)) as zipfile:
        zipfile.extractall(data_dir)
    dbf_name = path.basename(url).replace('zip', 'dbf')
    dbf_path = path.join(data_dir, dbf_name)
    run(['libreoffice', '--headless', '--convert-to', 'csv', '--outdir', data_dir, dbf_path])
    remove(dbf_path)


data_dir_path = 'data'

# create data directory if not exist
if not path.exists(data_dir_path):
    mkdir(data_dir_path)

download_lra_property_data(data_dir_path)
download_parcel_data(data_dir_path)
