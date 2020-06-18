from os import mkdir, path, remove
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://www.stlouis-mo.gov/government/departments/sldc/real-estate/lra-owned-property-full-list.cfm"

o = urlparse(url)
base_url = url.replace(o.path, "")

data_dir = "data"

# create data directory if not exist
if not path.exists(data_dir):
    mkdir(data_dir)

# get LRA page
page = requests.get(url)

# make a soup
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

        # read the xlsx file
        df = pd.read_excel(data_path)

        # change the extension to .csv
        csv_path = file_path.replace(".xlsx", ".csv")

        # store the csv file
        df.to_csv(csv_path, index=False)

        # remove the original xlsx file
        remove(file_path)
