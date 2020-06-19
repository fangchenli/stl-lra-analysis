from os import path, scandir

import pandas as pd

import googlemaps


def get_latlng(client, address):

    address_completion = ", St. Louis, MO, USA"
    geocode_result = googlemaps.client.geocode(client, address + address_completion)

    if not geocode_result:
        print("get none result")
        exit(1)
    else:
        return geocode_result[0]["geometry"]["location"]


api_key = "key"

# initialize a google map client
gmaps = googlemaps.Client(key=api_key)

with scandir("data") as it:

    for entry in it:

        data_path = path.join("data", entry.name)

        df = pd.read_csv(data_path)

        # use the google map api to get the lat
        df["latlng"] = df["Address"].map(lambda addr: get_latlng(gmaps, addr))

        df.to_csv(data_path, index=False)

        print(data_path, "is finished")
