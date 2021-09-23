"""Return metadata.json and count_kb.csv, count_eu.csv

see python3 query_kb.py -h
"""
import argparse
import concurrent.futures
import csv
import typing
from collections import defaultdict
import os
import itertools

import pandas as pd
import requests
import xmltodict
from tqdm import tqdm

from Metadata import Metadata

# CL arguments
parser = argparse.ArgumentParser(
    description="""Query KB apis and return metadata.json and count_kb.csv, count_eu.csv

    Requirements: europeana_catalogue.csv, as an output from catalogue.py, in the
    same dir as the query_kb.py

    Example:

        python3 query_kb.py -s 'allochtoon AND type=artikel'

            report query count, and save metadata.json in current dir reflecting query

        python3 query_kb.py -c queries_words.txt queries_dates.txt -save_dir=output_dir

            - updata output_dir/metadata.json, resulting from the every
                query combination of queries_words.txt and queries_dates.txt.
            - overwrite output_dir/count_kb.csv and output_dir/count_eu, with
              respect to the query combination of the newly passes queries only

        python3 query_kb.py -c queries_words.txt queries_dates.txt -m 200 -save_dir=output_dir

            As above, plus for every query combination, 200 are selected at random (or as many as available),
            metadata is retrieved and metadata.json updated to include this metadata.

    Output:

        metadata.json:
            A dictionary of urls to kb ocr records and associated data:
                * An entry is stored for all kb articles matching any query.
                * where an entry is randomnly selected as part of the -m query,
                metadata is appended to the record
                * a record of all previous queries is appended to the end of
                metadata.json

        metadata.json: {
            "http://resolver.kb.nl/resolve?urn=ddd:110546794:mpeg21:a0114:ocr": {
                "europeana_issue_id": "/9200359/BibliographicResource_3000115848627",
                "kb_issue_id": "ddd:110546794:mpeg21",
                "oai_issue_id": "DDD:ddd:110546794:mpeg21",
                "matching_queries": [
                    "kwinti AND date within \"1910-01-01 1919-12-31\" AND type=artikel"
                ],
                "kb_oai_metadata_queried": true,
                "kb_oai_metadata": {
                    "datestamp": "2021-01-06T07:57:47.279Z",
                    "title": "De Telegraaf",
                    "date": "1912-06-17",
                    "temporal": "Avond",
                    "publisher": "Dagblad De Telegraaf",
                    "spatial_distribution": "Landelijk",
                    "spatial_origin": "Amsterdam",
                    "language": [
                        "nl"
                    ]
                }
            },
            "http://resolver.kb.nl/resolve?urn=MMKB23:001819128:mpeg21:a00008:ocr": {
                "europeana_issue_id": null,
                "kb_issue_id": "MMKB23:001819128:mpeg21",
                "oai_issue_id": null,
                "matching_queries": [
                    "aboriginal AND date within \"1900-01-01 1909-12-31\" AND type=artikel"
                ],
                "kb_oai_metadata_queried": false,
                "kb_oai_metadata": {}
            },
            ...,
            "queries": [
                "kaukasisch AND date within \"1890-01-01 1899-12-31\" AND type=artikel",
                ...
            ]

        }

        count_kb.csv:
            A table of matching match counts of articles listed in the kb, jsru.kb.nl API

        count_eu.csv:
            A table of matching match counts of articles listed in the kb, whose parent issues are listed in the europeana database

    """,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

# query inputs

# required arguments - what is to be queried
query_group = parser.add_mutually_exclusive_group()
query_group.required = True

query_group.add_argument("-s", nargs=1, help="query passed via CL")
query_group.add_argument(
    "-w", nargs=1, help="path to txt file of line separated queries"
)
query_group.add_argument(
    "-c",
    nargs=2,
    help="path to 2 txt files of line separated query parts for which every combination is to be queried",
)

# other optional arguments
parser.add_argument("-m", nargs=1, default=["0"], help="")
parser.add_argument(
    "-save_dir",
    nargs=1,
    help="directory from which to import metadata.json and save metadata.json, and .csv",
)


def main():

    args = parser.parse_args()

    # location to save metadata.json, count_kb.csv, and count_eu.csv
    save_location = args.save_dir[0] + "/" if args.save_dir else ""
    # touch sav_dir
    if save_location != "":
        os.makedirs(os.path.dirname(save_location), exist_ok=True)

    # load metadata if exists or create new metadata object
    if args.save_dir:
        metadata = Metadata(save_location + "metadata.json")
    else:
        metadata = Metadata("metadata.json")

    # load eu_id, delpher_url pairs from europeana_catalogue.csv
    europeana_catalogue: typing.Generator = gen_csv_rows(
        "europeana_catalogue.csv", ignore_rows=[0]
    )

    # Build query iterable
    print("\tbuilding search queries")
    if args.s:
        search_queries: typing.List = args.s
    elif args.w:
        search_queries: typing.Generator[str] = gen_file_lines(args.w[0])
    elif args.c:
        search_queries: typing.Generator[tuple] = gen_file_lines_combinations(
            args.c
        )  # generator of (query_file_1_line_1, query_file_2_line_1) tuples for all possible combinations

    # tee copies 
    search_queries_t1, search_queries_t2 = itertools.tee(search_queries,2)

    print(
        "\n\tquery jsru.kb.nl for query-matching kb articles, and add article records to metadata.json, and record article counts by query"
    )

    # depending on query format ...
    if args.s or args.w:

        # dicts to store article counts
        count_eu = {}
        count_kb = {}

        # iterate over passed query contents
        for search_query in tqdm(search_queries_t1, desc="queries", leave=True):

            # ignore queries already included in metadata.json
            if search_query not in metadata.queries:
                print(f"\n\n\t{search_query}")

                kb_ocr_urls: typing.Generator = gen_kb_urls(
                    search_query
                )  # iterable of 'http://resolver.kb.nl/resolve?urn=ddd:010567709:mpeg21:a0493:ocr' items matching the query

                metadata.add_urls(
                    kb_ocr_urls, search_query
                )  # add any new ocr urls to metadata and/or associated queries with url

                metadata.add_europeana_ids(
                    europeana_catalogue
                )  # associate the europeana_id with the ocr url

            # from metadata.json, get a count of article matches for current query
            count_eu[search_query] = [metadata.get_europeana_match_count(search_query)]
            count_kb[search_query] = [metadata.get_kb_match_count(search_query)]

    elif args.c:

        headers = []
        count_eu = defaultdict(list)
        count_kb = defaultdict(list)

        # iterate over passed query content tuples
        for row, column in tqdm(search_queries_t1, desc="queries"):

            search_query: str = row + " AND " + column

            # only collect kb urls for metdata where not present in metadata
            if search_query not in metadata.queries:
                print(f"\n\n\t{search_query}")

                kb_ocr_urls: typing.Generator = gen_kb_urls(
                    search_query
                )  # iterable of 'http://resolver.kb.nl/resolve?urn=ddd:010567709:mpeg21:a0493:ocr' items matching the query

                metadata.add_urls(kb_ocr_urls, search_query)
                metadata.add_europeana_ids(europeana_catalogue)

            # from metadata.json, get a count of article matches for current query
            count_eu[column].append(metadata.get_europeana_match_count(search_query))
            count_kb[column].append(metadata.get_kb_match_count(search_query))

            if row not in headers:
                headers.append(row)

        count_eu[""] = headers
        count_kb[""] = headers

    # FINALLY

    # output query-article match counts, for arg.s terminal queries only
    if args.s:
        for q, c in count_kb.items():
            print(f"\n\n\t{q}:{c[0]} matching articles in kb records")
        for q, c in count_eu.items():
            print(f"\t{q}:{c[0]} matching articles in eu records")

    # save match counts
    pd.DataFrame.from_dict(count_eu).transpose().to_csv(save_location + "count_eu.csv")
    pd.DataFrame.from_dict(count_kb).transpose().to_csv(save_location + "count_kb.csv")

    #
    # if -m passed: randomnly sample n
    #
    if args.m[0] != "0":
        print(f"\n\n\tgetting random sample kb&eu records matching")
        if args.c:
            metadata.add_metadata(
                [q1 + " AND " + q2 for q1, q2 in search_queries_t2],
                int(args.m[0]),
            )
        else:
            metadata.add_metadata(search_queries_t2, int(args.m[0]))

    #
    # save updated metadata.json
    #
    metadata.to_json(save_location + "metadata.json")


def gen_kb_urls(query: str) -> typing.Generator:
    """Return an generator of urls to KB ocr files matching a query.

    e.g., http://resolver.kb.nl/resolve?urn=ABCDDD:010842133:mpeg21:a0368:ocr

    Args:
        query (str): query to pass to jsru.kb.nl .... e.g., Allochtoon
    """

    base_url = (
        "http://jsru.kb.nl/sru/sru?version=1.2"
        + "&operation=searchRetrieve"
        + "&x-collection=DDD_artikel&"
        + "recordSchema=dc"
    )

    # get number of records matching query, n
    response = get_response(
        base_url + "&startRecord=1&maximumRecords=1" + f"&query=({query})"
    )
    response = xmltodict.parse(response.text)
    n: int = int(response["srw:searchRetrieveResponse"]["srw:numberOfRecords"])

    # get urls for each sub-page of the metadata index
    index_URLS = (
        base_url + f"&startRecord={i}&maximumRecords=1000" + f"&query=({query})"
        for i in range(1, n, 1000)
    )

    # for each metadata index sub-page request response, transform xml to dict, iterate over dicts and yield record ocr url
    for url, response in gen_threaded(index_URLS, f=get_response, max_workers=50):
        if response is not None:
            response_as_dict = xmltodict.parse(response.text)
            records: typing.List = response_as_dict["srw:searchRetrieveResponse"][
                "srw:records"
            ]["srw:record"]
            for r in records:
                yield r["srw:recordData"]["dc:identifier"]


def gen_threaded(
    iterable: typing.Iterable,
    *,
    f: typing.Callable,
    max_workers: int = None,
    chunk_size=None,
) -> typing.Generator:
    """Return a generator yielding tuple (item, f(item)), for passed iterable.

    For I/O intensive processes.
    see: https://docs.python.org/3/library/concurrent.futures.html

    Examples:
        g = gen_threaded(urls, f=get_response)
        url, response = next(g)

        g = gen_threaded(urls, f=partial(get_response, max_attempts = 1))
        url, response = next(g)

    Args:
        iter [iterable]:
        f [callable]: Does not accept lambdas
        chunk_size (int): concurrent.futures is greedy and will evaluate all of
            the iterable at once. chunk_size limits the length of iterable
            evaluated at any one time (and hence, loaded into memory).
            [default: chunk_size=len(iterable)]
    """
    # concurrent.futures will greedily evaluate and store in memory, hence
    # chunking to limit the scale of greedy evaluation
    if chunk_size:
        chunks = gen_chunks(iterable, chunk_size)
    else:
        # chunks = map(lambda i: iterable, range(1))  # chunks contains a single chunk
        chunks = [iterable]

    for chunk in chunks:

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

            future_items = {executor.submit(f, item): item for item in chunk}

            for future in concurrent.futures.as_completed(future_items):
                yield (future_items[future], future.result())


def get_response(
    url: str, *, max_attempts=5, **request_kwargs
) -> typing.Union[requests.Response, None]:
    """Return the response.

    Tries to get response max_attempts number of times, otherwise return None

    Args:
        url (str): url string to be retrieved
        max_attemps (int): number of request attempts for same url
        request_kwargs (dict): kwargs passed to requests.get()
            timeout = 10 [default]

    E.g.,
        r = get_response(url, max_attempts=2, timeout=10)
        r = xmltodict.parse(r.text)
        # or
        r = json.load(r.text)
    """
    # ensure requests.get(timeout=10) default unless over-ridden by kwargs
    if "timeout" in request_kwargs:
        pass
    else:
        request_kwargs["timeout"] = 10

    # try max_attempts times
    for count, x in enumerate(range(max_attempts)):
        try:
            response = requests.get(url, **request_kwargs)
            return response
        except:
            time.sleep(0.01)

    # if count exceeded
    return None


def gen_file_lines(path: str, *, strip: list = ["\n"]) -> typing.Generator:
    """Return a generator yielding successive file lines.

    Args:
        path (str): path to txt file
        strip (list): a list of strings to be recursively stripped from each line

    Example:
        gen_file_lines(path, strip = [])
    """
    with open(path, "r") as f:
        for line in f:

            if strip:
                # recursively apply strip(), for each entry in strip arg
                state = line
                for entry in strip:
                    state = state.strip(entry)
                # yield stripped line
                yield state
            else:
                yield line


def gen_file_lines_combinations(paths: typing.Iterable) -> typing.Generator:
    """Return a generator yielding combination tuples of lines between files.

        Strips lines of '\n'.

        Args:
            paths: iterable of file paths for which to find combinations of their
            respective contents
    e
        Example:

        E.g., for 2 files, each with 2 lines:
        fileX | fileY
            A |     1
            B |     2
        Generator yields: (A, 1), (A, 2), (B, 1), (B, 2)
    """
    g = (gen_file_lines(path) for path in paths)

    for combination in itertools.product(*g):
        yield combination


def gen_csv_rows(path: str, *, ignore_rows: typing.List = []) -> typing.Generator:
    """Return a generator yielding successive csv rows.

    Will ignore row indices specified in ignore_rows arg.

    Args:
        path (str): path to csv
        ignore_rows (list): E.g., title row = [0]
    """
    with open(path, "r") as f:
        for index, line in enumerate(csv.reader(f)):
            if index not in ignore_rows:
                yield line


def get_response(
    url: str, *, max_attempts=5, **request_kwargs
) -> typing.Union[requests.Response, None]:
    """Return the response.

    Tries to get response max_attempts number of times, otherwise return None

    Args:
        url (str): url string to be retrieved
        max_attemps (int): number of request attempts for same url
        request_kwargs (dict): kwargs passed to requests.get()
            timeout = 10 [default]

    E.g.,
        r = get_response(url, max_attempts=2, timeout=10)
        r = xmltodict.parse(r.text)
        # or
        r = json.load(r.text)
    """
    # ensure requests.get(timeout=10) default unless over-ridden by kwargs
    if "timeout" in request_kwargs:
        pass
    else:
        request_kwargs["timeout"] = 10

    # try max_attempts times
    for count, x in enumerate(range(max_attempts)):
        try:
            response = requests.get(url, **request_kwargs)
            return response
        except:
            time.sleep(0.01)

    # if count exceeded
    return None


if __name__ == "__main__":
    main()
