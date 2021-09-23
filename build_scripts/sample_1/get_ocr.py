"""
Extract a subset of metadata.json for those newspaper items with metadata records
"""

import argparse
import json
import os
import random
import time
import typing
from collections import OrderedDict

import requests
import xmltodict
from tqdm.contrib.concurrent import thread_map

parser = argparse.ArgumentParser(
    description="""For those records in metadata.json which which oai metadata exists: retrieve ocr text for a specified sample size, and save as a new container.

    Example:
        python3 get_ocr.py -f contentious_words/metadata.json -all -save_dir contentious_words 

            extract ocr text for all records with metadata in metadata.json and
            output ocr.json in contentious_words folder.

        python3 get_ocr.py -f contentious_words/metadata.json -s 1000 -save_dir contentious_words

            extract ocr text for 1000 random sample records with metadata in
            metadata.json and output ocr.json in contentious_words folder.

    Output:

        ocr.json : [
            [
                "http://resolver.kb.nl/resolve?urn=ddd:110540397:mpeg21:a0037:ocr",
                {
                    "europeana_issue_id": "/9200359/BibliographicResource_3000115832584",
                    "kb_issue_id": "ddd:110540397:mpeg21",
                    "oai_issue_id": "DDD:ddd:110540397:mpeg21",
                    "matching_queries": [
                        "aboriginal AND date within \"1890-01-01 1899-12-31\" AND type=artikel"
                    ],
                    "kb_oai_metadata_queried": true,
                    "kb_oai_metadata": {
                        "datestamp": "2021-01-06T07:18:08.959Z",
                        "title": "De Telegraaf",
                        "date": "1896-08-08",
                        "temporal": "De Telegraaf",
                        "publisher": "Dagblad De Telegraaf",
                        "spatial_distribution": "Landelijk",
                        "spatial_origin": "Amsterdam",
                        "language": [
                            "nl"
                        ]
                    }
                },
                {
                    "text": {
                        "title": "Cricket.",
                        "p": "•i eigenaardig geval deed zich voor in en trüd tosseben lint Lancashirs on i h ickburn. De -ast Lancaahire m aiir-'h 9 wtokets voor 70 v-1 werd da 10e batsman gewond en verli „'I Ime* werd kort daarna geroejieu, d ich op 't zelfdi .v keerde de speler scheidsrechters verklaarden hot, spel als g .iro beweerde ge.. Uia iieb dat de batsman gerechtigd was do laatste over geheel uit te spolon. * * * De moest bekende, rocords op het gobio I i in worpen met don cricketbal, zyn de volg 140 yards door , Bioly the Aboriginal\" in Australië in l • ■ ard door Forbas, _ : toor . , Australië, 128 yard inch door Grane, Australië. (De Athkit.}. Eergisteren maakte Middleaex to Londen 279 tegen Gloucestershire'a 48 *. 3 wickets, T. C. 0 Brien : 68."
                    }
                }
            ],
            ...
        ]

    """,
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument("-f", nargs=1, help="file path to metadata.json")

selection_group = parser.add_mutually_exclusive_group()
selection_group.required = True
selection_group.add_argument("-all", action="store_true", default=False)
selection_group.add_argument("-s", nargs=1, help="number of random extracts to extract")

parser.add_argument("-o", nargs=1, help="dir to save ocr.json output")


def main():

    args = parser.parse_args()

    # deal with location if specified
    save_folder = args.o[0] + "/" if args.o else ""

    # import the saved metadata
    print("import metadata.json")
    metadata = get_json(args.f[0])
    queries = metadata.pop("queries")  # useless info for this task

    # get the metadata subset with metadata
    metadata_queried = {
        url: data
        for url, data in metadata.items()
        if data["kb_oai_metadata_queried"] is not False
    }

    # select a random sample of metadata records (or all)
    if args.all:
        print(f"sample size = {len(metadata_queried)}")
        sample: typing.List = metadata_queried.items()
    else:
        print(f"sample size = {len(int(args.s[0]))}")
        sample: typing.List = random.sample(metadata_queried.items(), int(args.s[0]))
    # sample = [(url, data), ...]

    # for each selected metadata record, get ocr
    print("retrieve ocr text for article in metadata.json samples for metadata")
    output: typing.List = thread_map(get_ocr, sample)
    # output = [(url, metadata, ocr), ...]

    # output
    to_json(output, save_folder + "ocr.json")


def get_ocr(metadata_record: typing.Tuple):
    url, metadata = metadata_record
    ocr = get_xml(url)

    return (url, metadata, ocr)


def get_xml(url: str) -> OrderedDict:
    """Return xml query response as a dict."""

    # loop until ...
    count = 0
    while count < 5:
        try:
            response = requests.get(url, timeout=5)
            d: OrderedDict = xmltodict.parse(
                response.text.encode("latin1").decode("utf8")
            )
            return d
        except:
            time.sleep(0.01)
            count += 1

    return False


def to_json(container, filename: str) -> typing.NoReturn:
    with open(filename, "w") as f:
        json.dump(container, f, indent=4, ensure_ascii=False)


def get_json(filename: str):
    with open(filename, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
