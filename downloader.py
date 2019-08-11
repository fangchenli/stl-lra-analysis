from os import path, mkdir, remove

from bs4 import BeautifulSoup
import pandas as pd
import requests

base_url = 'https://www.stlouis-mo.gov'

url = 'https://www.stlouis-mo.gov/government/departments/sldc/real-estate/lra-owned-property-full-list.cfm'

data_dir = 'data'

# create data directory if not exist
if not path.exists(data_dir):
    mkdir(data_dir)

# get LRA page
page = requests.get(url)

# make a soup
soup = BeautifulSoup(page.content, 'html.parser')

# find all "a" tags with href
a_tags = soup.find_all('a', href=True)

# download xls files and store to csv format
for a_tag in a_tags:
    href = a_tag['href']

    if href.endswith('.xls'):

        # use + to join the path since the href start with a back slash, path.join() doesn't work in this case
        data_path = base_url + href

        # get the file
        r = requests.get(data_path, allow_redirects=True)

        base_name = path.basename(data_path)

        file_path = path.join(data_dir, base_name)

        # write the content of the request to local dir
        with open(file_path, 'wb') as f:
            f.write(r.content)

        # read the xls file
        df = pd.read_excel(data_path)

        # change the extension to .csv
        csv_path = file_path.replace('.xls', '.csv')

        # store the csv file
        df.to_csv(csv_path, index=False)

        # remove the original xls file
        remove(file_path)
