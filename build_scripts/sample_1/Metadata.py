import itertools
import json
import os
import random
import re
import time
import typing
from collections import defaultdict
from multiprocessing.pool import ThreadPool

import requests
import xmltodict


class Metadata(object):
    """Create an object for assembly/ storage of KB/ europeana newspaper article metadata.

    Loads self.metadata and self.queries from metadata.json (if available).
    otherwise creates new.

    Args:
        metadata_file (str): filepath to metadata.json [default:'metadata.json']
    """

    def __init__(self, metadata_file: str = "metadata.json"):
        """
        Properties:

            self.metadata['http://resolver.kb.nl/resolve?urn=ddd:010567709:mpeg21:a0493:ocr'] = {
                    "europeana_issue_id": "/9200359/BibliographicResource_3000116007227"
                    "kb_issue_id": 'ddd:010567709:mpeg21'  # referenced in europeana metadata
                    "oai_issue_id": 'DDD:ddd:010567709:mpeg21',
                    "matching_queries": ['berber'],
                    "kb_oai_metadata_queried": False
                    "kb_oai_metadata": {
                        "title": # from kb.nl/mdo/oai,
                        "date": # from kb.nl/mdo/oai ,
                        "temporal": # from kb.nl/mdo/oai,
                        "publisher": # from kb.nl/mdo/oai,
                        "spatial_distribution": # from kb.nl/mdo/oai,
                        "spatial_origin": # from kb.nl/mdo/oai,
                        "language": [] # from kb.nl/mdo/oai,
                        "datestamp: # from kb.nl/mdo/oai,
                    }
                }
            self.queries = set(['blank', 'berber', ...])
        """
        self.metadata: typing.Dict = {}
        self.queries = set([])
        if metadata_file:
            if os.path.exists(metadata_file):
                print("import metadata.json")
                self.metadata: typing.Dict = get_json(metadata_file)
                self.queries = set(self.metadata.pop("queries"))

    def add_urls(self, ocr_urls: typing.Iterable, query: str):
        """Update self.metadata with new kb article entries (key=kb ocr url) and/or update to record matching query

        Args:
            ocr_urls (Iterable): http://resolver.kb.nl/resolve?urn=ABCDDD:010842133:mpeg21:a0368:ocr
            query (str): the query which ocr_urls matches against
        """

        for ocr_url in ocr_urls:

            # create new record for unseen urls
            if ocr_url not in self.metadata.keys():
                self.metadata[ocr_url] = {
                    "europeana_issue_id": None,
                    "kb_issue_id": re.search(".+=(.+):a.+:ocr", ocr_url).group(1),
                    "oai_issue_id": get_oai_issue_id(
                        ocr_url
                    ),  # returns None if not 'ddd' (europeana included set)
                    "matching_queries": [],
                    "kb_oai_metadata_queried": False,
                    "kb_oai_metadata": {},
                }

            # attribute matching query for new and old records (if query unseen)
            if query not in self.metadata[ocr_url]["matching_queries"]:
                self.metadata[ocr_url]["matching_queries"].append(query)

        # add query to self.queries set
        self.queries.add(query)

    def add_europeana_ids(self, europeana_catalogue: typing.Iterable):
        """For each url/record in self.metadata attach correct europeana id.

        Args:
            europeana_catalogue (iterable):
        """

        hash = defaultdict(list)  # parent newspaper id: [article_id, article2_id, ...]
        for url, data in self.metadata.items():
            hash[data["kb_issue_id"]].append(url)

        for eu_id, isShownAt in europeana_catalogue:
            kb_id: str = re.search(".+=(.+)", isShownAt).group(1)

            if kb_id in hash.keys():
                for url in hash[kb_id]:
                    self.metadata[url]["europeana_issue_id"] = eu_id

    def add_metadata(self, queries, n):
        """Add metadata for n random articles matching a query (previously unqueried, with europeana_issue_id)

        Note: only those urls previously unqueried form oai metadata, part of
        europeana form part of the pool for random selection.
        """

        url_selection: typing.Generator = self.get_url_random_selection(queries, n)

        # in parallel, get oai record for url, and update self.metadata
        with ThreadPool(50) as p:
            p.map(self.add_metadata_map, url_selection)

    def get_url_random_selection(
        self, queries: typing.Iterable, n: int
    ) -> typing.Generator:
        """Return a RANDOM sample generator of 'n' urls w/o metadata, wrt., each query.

        Note: only those urls previously unqueried form oai metadata, part of
        europeana form part of the pool for random selection.

        Args:
            queries (iterable):
            n (int): number of urls per query to retrieve
        """
        queries_set = set(queries)

        # ------
        # assemble a dict of {query:list of potential urls, ...}, wrt., passed queries
        #   - potentials are previously unqueried (for metadata) and have a europeana id.
        # -----
        potential = defaultdict(list)
        for url in self.metadata.keys():

            incommon_queries = queries_set.intersection(
                set(self.metadata[url]["matching_queries"])
            )
            if (
                self.metadata[url]["kb_oai_metadata_queried"] is False
                and self.metadata[url]["europeana_issue_id"] is not None
                # and self.metadata[url]["oai_issue_id"] is not None  # already implied by above condition, since when oai_issue_id = None, i.e, not a ddd item, them not present in europeana
                and bool(incommon_queries)
            ):
                for q in incommon_queries:
                    potential[q].append(url)

        # ------
        # for each query, randomnly sample w/o replacement and yield
        # ------
        for query in queries:
            for url in random.sample(potential[query], k=min(n, len(potential[query]))):
                yield url

    def add_metadata_map(self, url):

        url, record = get_oai_record(url, self.metadata[url]["oai_issue_id"])

        if record:
            self.metadata[url]["kb_oai_metadata_queried"] = True
            self.metadata[url]["kb_oai_metadata"]["datestamp"] = record["header"][
                "datestamp"
            ]

            m = record["metadata"]["didl:DIDL"]["didl:Item"]["didl:Component"][0][
                "didl:Resource"
            ]["srw_dc:dcx"]

            self.metadata[url]["kb_oai_metadata"]["title"] = m["dc:title"]
            self.metadata[url]["kb_oai_metadata"]["date"] = m["dc:date"]
            self.metadata[url]["kb_oai_metadata"]["temporal"] = m["dcterms:temporal"]
            self.metadata[url]["kb_oai_metadata"]["publisher"] = m["dc:publisher"]
            self.metadata[url]["kb_oai_metadata"]["spatial_distribution"] = m[
                "dcterms:spatial"
            ][0]
            self.metadata[url]["kb_oai_metadata"]["spatial_origin"] = m[
                "dcterms:spatial"
            ][1]["#text"]

            # language edge cases
            self.metadata[url]["kb_oai_metadata"]["language"] = []
            entry = m["dc:language"]
            if type(entry) == list:
                for i in entry:
                    self.metadata[url]["kb_oai_metadata"]["language"].append(i["#text"])
            else:
                self.metadata[url]["kb_oai_metadata"]["language"].append(entry["#text"])

    def to_json(self, save_file: str = "metadata.json") -> typing.NoReturn:

        # incorporate queries into self.metadata for saving
        self.metadata["queries"] = list(self.queries)  # save queries

        print("saving metadata update to metadata.json")
        to_json(self.metadata, save_file)
        print('\nsee "metadata.json" for updates to queried metadata')

    def get_europeana_match_count(self, query: str) -> int:

        count = 0
        for article_url, data in self.metadata.items():
            if (
                query in data["matching_queries"]
                and data["europeana_issue_id"] is not None
            ):
                count += 1

        return count

    def get_kb_match_count(self, query: str) -> int:

        count = 0
        for article_url, data in self.metadata.items():
            if query in data["matching_queries"]:
                count += 1

        return count


def get_oai_issue_id(article_url) -> typing.Union[str, None]:
    """Return the kb oai_issue_id  of any 'ddd' subset newspaper issue (only ddd is in europeana)."""

    part1, part2 = re.search(r".*=(.+?):(.+):a.+", article_url).groups()

    if part1 == "ddd":
        return ":".join(["DDD", part1, part2])
    else:
        return None


def get_oai_record(url: str, oai_issue_id: str) -> dict:
    """Return [url, oai_metadata] for passed [url, oai_issue_id] identifiers.

    Note: oai record retrived via KB oai api
    Note: if no record, returns [url, None]
    """

    base_url = "http://services.kb.nl/mdo/oai/e3c39382-fe3c-421f-bda7-6feb59d11211/?verb=GetRecord&metadataPrefix=didl"

    # get the record from kb oai api
    response = get_response(base_url + "&identifier=" + oai_issue_id)

    if response:
        record = xmltodict.parse(response.text)
        return [url, record["OAI-PMH"]["GetRecord"]["record"]]
    else:
        return [url, None]


def to_json(container, filename: str) -> typing.NoReturn:
    with open(filename, "w") as f:
        json.dump(container, f, indent=4)


def get_json(filename: str):
    with open(filename, "r") as f:
        return json.load(f)


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
