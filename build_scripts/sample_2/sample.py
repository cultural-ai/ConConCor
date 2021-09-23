"""
Stratified sampling of extract, by query and spatial distribution, sampled by
P(extract weights). see "python3 sample.py -h"
I.e.: 
    * For specified sampling criteria, create a generator of samples, sampled
    by P(extract) weighting. 
    * Cycle through randomly shuffled queries, selecting a random extract wrt.,
    query until -N criteria is satisfied
"""

import argparse
import itertools
import json
import os
import random
import re
import typing
from collections import defaultdict

import numpy as np
import pandas as pd
from tqdm import tqdm

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description="""Stratified sampling of extracts according to P(extract)

    Note: extra to the input criteria, extracts are limited to an average of
    200 characters per sentence.

    Example:
            python3 sample.py -data ../score/alternative_words/scored.json -q sampling_criteria/alternative_criteria.txt -s sampling_criteria/spatial.txt -a 2 -n 12 -N 1200 -sav_dir contentious_words
    """,
)
parser.add_argument(
    "-q",
    nargs=1,
    help="The relative path to a .txt file containing line-separated queries to sample",
    required=True,
)
parser.add_argument(
    "-s",
    nargs=1,
    help="The relative path to a .txt file containing line-separated spatial distributions to sample ",
    required=True,
)
parser.add_argument(
    "-a",
    nargs=1,
    help="The number of sentences before and after the sentence of the target word required. e.g., 2, results in 5-sentnence extracts",
    required=True,
    type=int,
)
parser.add_argument(
    "-n",
    nargs=1,
    help="number of extract to retrieve for every -q -a combination",
    required=True,
    type=int,
)
parser.add_argument(
    "-N",
    nargs=1,
    help="total number of extracts to sample",
    required=True,
    type=int,
)
parser.add_argument(
    "-sav_dir", nargs=1, help="location to save output sample of extracts", default=""
)

parser.add_argument(
    "-data",
    nargs=1,
    help="""The relative path to input data.

    Example structure
    [
        [
            "http://resolver.kb.nl/resolve?urn=ddd:110540397:mpeg21:a0037:ocr",
            {
                "oai_issue_id": "DDD:ddd:110540397:mpeg21",
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
                },
                "matching_queries": [
                    "aboriginal AND date within \"1890-01-01 1899-12-31\" AND type=artikel"
                ],
                "europeana_issue_id": "/9200359/BibliographicResource_3000115832584",
                "kb_issue_id": "ddd:110540397:mpeg21",
                "kb_oai_metadata_queried": true
            },
            {
                "text": {
                    "title": "Cricket.",
                    "p": "•i eigenaardig geval deed zich voor in en trüd tosseben lint Lancashirs on i h ickburn.
                    "s": ["•i eigenaardig geval deed zich voor in en trüd tosseben lint Lancashirs on i h ickburn."],
                    "neg_log_probability": [71.102],
                    ...
            }
        ],
        ...
    ]

    """,
    required=True,
)


def main():

    args = parser.parse_args()
    if args.s[0] == "":
        sav_dir = ""
    else:
        sav_dir = args.sav_dir[0] + "/"
        os.makedirs(os.path.dirname(sav_dir), exist_ok=True)

    # ------
    # get the scored sentences, find potential extracts and append
    # ------

    # get the input json of articles information
    print(f"loading {args.data[0]}")
    articles: list = get_json(
        args.data[0]
    )  # [[ocr_url:str, metadata:dict, ocr:str], ...]

    # For each article, identify extracts and append to article records (in-place)
    print(f"collecting all extracts with {args.a[0]} sentences above and below")
    add_extracts(articles, adjacent=args.a[0])

    # -------
    # assemble sampling criteria
    # -------

    print("Assembling sampling criteria")
    sampling_criteria: typing.Generator = gen_file_lines_combinations(
        [args.q[0], args.s[0]]
    )  # queries of

    num_samples_per_query = args.n[0]
    max_extract_chars = (
        2 * args.a[0] + 1
    ) * 200  # i.e., max 200 chars per sentence on average

    sampling_criteria: typing.Iterator = (
        list(i) + [num_samples_per_query, max_extract_chars] for i in sampling_criteria
    )  # see description, below
    # sampling_criteria is a generator of tuples, defining our sampling criteria, i.e., :
    #   (
    #       'kaukasisch AND date within "1890-01-01 1899-12-31" AND type=artikel',
    #       'Landelijk',
    #       4,
    #       1000
    #   )

    # ------
    # get stratified samples according to 'sampling_criteria' - randomly sampled according to P(extract) weighting
    # ------
    print("Sampling ...")

    sampled_extracts: typing.Generator = strat_sample(
        sampling_criteria, articles
    )  # sampled_extracts  [(url, metadata, extract, corresponding query), ...]

    # -------
    # further refine samples to meet -N requirement
    # -------

    sampled_by_query = defaultdict(list)  # {query:[(url, metadata, extract), ...]}
    for extract in sampled_extracts:
        query = extract[3]
        data = extract[:3]  # [url, metadata, extract]
        sampled_by_query[query].append(data)  # {query:[(url, metadata, extract), ...]}

    # get list of randonmnly shuffled query words
    shuffled_queries = list(sampled_by_query.keys())
    random.shuffle(
        shuffled_queries
    )  # queries randomly shuffled such that none favoured

    print(f"number of query variations = {len(shuffled_queries)}")
    print(
        f"number of extracts from which to sample {args.N[0]} = {sum([len(v) for k,v in sampled_by_query.items()])}"
    )

    # itereate over-randomly shuffled queries, and sample a single w/o replacement until all -N retrieved
    new_data = {"url": [], "query": [], "extract": [], "metadata": []}
    index = 0
    while len(new_data["url"]) < args.N[0]:

        if len(new_data["url"]) % 100 == 0:
            print(len(new_data["url"]))

        # get the next data point, going in order of shuffled_queries where available
        while True:

            query = shuffled_queries[index]

            if len(sampled_by_query[query]) > 0:

                # pop a random extract associated with random query, and then append to new store
                data = sampled_by_query[query].pop(
                    random.randint(0, len(sampled_by_query[query]) - 1)
                )
                index = index + 1 if index < len(shuffled_queries) - 1 else 0
                break
            else:
                index = index + 1 if index < len(shuffled_queries) - 1 else 0

        # apppend that datapoint
        new_data["url"].append(data[0])
        new_data["extract"].append(data[2])
        new_data["query"].append(query.split(" AND ")[0])
        data[1]["matching_queries"] = [
            query
        ]  # update extract metadata to reflect matched query
        new_data["metadata"].append(data[1])

    print("Saving ...")

    df = pd.DataFrame.from_dict(new_data)
    df.to_csv(sav_dir + "sampled.csv")

    # output sample to json
    new_data_as_json = [
        [
            new_data["url"][i],
            new_data["metadata"][i],
            new_data["extract"][i],
            new_data["query"][i],
        ]
        for i in range(len(new_data["url"]))
    ]
    to_json(new_data_as_json, sav_dir + "sampled.json")


def add_extracts(articles: typing.List, *, adjacent: int) -> typing.NoReturn:
    """Get and append (in-place) at 'articles' a list of potential article extracts.

    Args:
        articles (List): [(url, metadata, text), ...]
        n (int): minimum number of sentences required either side of extract.
                    E.g., n=1 for 3 sentence extracts, n=2 for 5

    Potential extracts added at:
        articles[url][i]['text']['extracts']
            = [('query', 'matching n sentence extract', est P(extract)), ...]
    """

    # interate over articles
    for url, metadata, split_sents, split_sents_nlls in get_articles(articles):

        article_extracts = []  # store collected extracts

        # identify (and pull) each extract on record ocr that matches a query
        for query in metadata["matching_queries"]:

            # NEED TO REWORK and make regex
            match_word: str = query.split(" AND ")[0]

            for extract in get_blocks(
                split_sents,
                split_sents_nlls,
                adjacent=adjacent,
                query=query,
                target=match_word,
            ):
                article_extracts.append(extract)

        articles[url][2]["text"]["extracts"] = article_extracts


def get_articles(articles: typing.Iterable) -> typing.Generator:
    """Yield the article info (url, metadata, split_sents, split_sents_NLLs)."""

    for url, article in enumerate(articles):

        metadata: typing.Dict = article[1]
        split_sents: typing.List = article[2]["text"]["s"]  # CHECK!
        split_sents_nlls: typing.List = article[2]["text"][
            "neg_log_probability"
        ]  # CHECK!

        yield (url, metadata, split_sents, split_sents_nlls)


def get_blocks(
    split_sents: typing.List,
    split_sents_nlls: typing.List,
    *,
    query: str,
    target: str,
    adjacent: int,
) -> typing.Generator:
    """yield an article's potential extracts in the form (query, extract, est P(extract)).

    Args:
        split_sents: e.g., ['de eerste zin', 'the 2nd sentence', ...]
        target: e.g., 'allochtoon'
        adjacent: the number of sentences needed above & below the sentence
            containing the target word
    """

    for index, sent in enumerate(split_sents):
        if re.search(target, sent, re.IGNORECASE):
            # we ignore those matches without a preceeding & following sentences
            if index < adjacent:
                pass
            elif index > len(split_sents) - 1 - adjacent:
                pass
            else:
                yield (
                    query,
                    "\n\n".join(split_sents[index - adjacent : index + adjacent + 1]),
                    sum(
                        split_sents_nlls[index - adjacent : index + adjacent + 1],
                    ),
                )


def scale_weights(l: typing.List) -> typing.List:
    """Return a normalised version of distribution"""
    epsilon = 1e-6
    return (np.array(l) + epsilon) / sum(np.array(l) + epsilon)


def strat_sample(criteria: typing.Iterable, articles: typing.List) -> typing.Generator:
    """Return a generator of samples [(url, metadata, extract, query), ... ].

    where each generated sample fulfilling each criterion in criteria,
    randomn selection weighted by P(sentence).

    Args:
        criteria (iterable): a list of tuples of
            (query, spatial distribution criteria, number of samples, max number of chars in extracts)
        articles (list): list of [url, metadata, text] of articles
    """

    returned = []

    # interate over each sampling criterion
    for c_query, c_spatial, n, max_chars in criteria:

        # ------
        # get a list of ALL potential extracts which meet the current criterion
        #   i.e., momentarity ignoring 'n' criteria
        # ------
        extracts_meeting_criterion: typing.List = []  # [(url, m, extract, score), ...]

        # iterate over articles
        for url, m, text_info in articles:

            article_spatial: str = m["kb_oai_metadata"]["spatial_distribution"]
            article_extracts = text_info["text"]["extracts"]

            # interate over extracts in article
            for extract_q, extract_text, extract_score in article_extracts:
                if (
                    extract_q == c_query
                    and article_spatial == c_spatial
                    and len(extract_text) <= max_chars
                ):
                    extracts_meeting_criterion.append(
                        (url, m, extract_text, extract_score)
                    )

        # ------
        # from our potential extracts meeting query, spatial_distribution and max_char criteria
        # randomnly sample (w/o replacement) n extracts weighted by P(extract)
        # ------
        if len(extracts_meeting_criterion) > 0:
            urls, metadata, extracts, extracts_nlls = zip(*extracts_meeting_criterion)

            # sample n extracts, w/o replacement (or fewer if unavailable)
            sample_indices = np.random.choice(
                range(len(urls)),
                size=min(n, len(extracts_meeting_criterion)),
                p=scale_weights(np.exp(-np.array(extracts_nlls))),
                replace=False,
            )

            # successively yield
            for index in sample_indices:
                yield (urls[index], metadata[index], extracts[index], c_query)

    return returned


def get_json(filename: str):
    with open(filename, "r") as f:
        return json.load(f)


def to_json(container, filename: str) -> typing.NoReturn:
    with open(filename, "w") as f:
        json.dump(container, f, indent=4, ensure_ascii=False)


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


if __name__ == "__main__":
    main()
