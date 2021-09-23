"""
Catalogue all europeana newspaper issues matching query=DATA_PROVIDER:"National Library of the Netherlands"&theme=newspaper

see catalogue.py -h

"""
import argparse
import json
import os
import time
import typing
import urllib

import pandas as pd
import requests
from tqdm import tqdm

parser = argparse.ArgumentParser(
    description="""Output europeana_catalogue.csv in current dir: a csv of pairs of europeana_id, delpher link for all newspaper issues returned by query:

    https://api.europeana.eu/record/v2/search.json?wskey={pass_key}&query=DATA_PROVIDER:\"National Library of the Netherlands\"&theme=newspaper

    Example:

        python3 catalogue.py

    Output:

        eu_id, isShownAt
        /9200359/BibliographicResource_3000116007227, http://kranten.delpher.nl/nl/view/index?image=ddd:110612753:mpeg21
    """,
    formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument("password", nargs=1, type=str)


def main():

    args = parser.parse_args()

    sav_file = "europeana_catalogue.csv"
    if os.path.exists(sav_file):  # do not overwrite existing output

        print(f"{sav_file} exists ... aborting")

    else:

        items_per_page = 100  # the maximum items that can be shown for a given request to api.europeana.eu
        base_url = f'https://api.europeana.eu/record/v2/search.json?wskey={args["password"]}&query=DATA_PROVIDER:"National Library of the Netherlands"&theme=newspaper&rows={items_per_page}'

        df = pd.DataFrame(
            columns=["eu_id", "isShownAt"]
        )  # new dataframe for storing pairs of eu_id, isShownAt values

        # iterate over each newspaper issue metadata in europeana.api query response, and add europeana id and delpher link (which contains kb _id) to df.
        newspapers_metadata = iter_items(base_url, items_per_page)
        for newspaper_metadata in tqdm(newspapers_metadata):
            row = [newspaper_metadata["id"], newspaper_metadata["edmIsShownAt"][0]]
            df.loc[len(df)] = row

        with open(sav_file, "w") as f:
            df.to_csv(f, index=False)


def iter_items(base_url: str, items_per_page: int) -> typing.Generator:
    """Return a Generator of metadata dicts for api.europeana.eu items matching base url.

        Sifts over subsequent pages corresponding to base_url

    Args:
        base_url: string of request url
        items_per_page: int denoting number of record items requested by response page.
    """
    n_items: int = int(get_response(base_url + "&start=1")["totalResults"])

    cursor: str = "*"
    for start in range(1, n_items, items_per_page):
        response: typing.Dict = get_response(base_url + f"&cursor={cursor}")
        cursor = urllib.parse.quote(response["nextCursor"])

        for item in response["items"]:
            yield item


def get_response(query: str) -> typing.Dict:
    """Return (json) query response as a dict.

    loop until a response is returned if request timeout
    """
    response = False
    while response is False:
        try:
            response = requests.get(query, timeout=10)
            d = json.loads(response.text)
            return d
        except:
            time.sleep(0.01)


if __name__ == "__main__":
    main()
