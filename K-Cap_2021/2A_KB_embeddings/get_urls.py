"""
Randomnly sample ocr urls from KB jsru database.

process:
    * i.e., article urls matching a query are split over multiple pages when a query is passed.  Urls are sampled by, i) imagining urls as splits of 1000 articles wide, sampling 1000 of these splits and taking 100 per split. This is done for each query. Hence, 100,000 per query are sampled.
"""


import concurrent.futures
import itertools
import os
import random
import time
import typing
from pprint import pp

import pydash
import requests
import xmltodict
from tqdm import tqdm


def main():

    # USER-SPECIFIED INPUTS

    split_width = 1000  # width of jsru split wrt., query
    n_splits = 1000  # number of splits to randomly sample
    per_split = 100  # number of urls to randomly sample per randomnly sampled split

    queries = [
        'type=artikel AND date within "1890-01-01 1899-12-31"',
        'type=artikel AND date within "1900-01-01 1909-12-31"',
        'type=artikel AND date within "1910-01-01 1919-12-31"',
        'type=artikel AND date within "1920-01-01 1929-12-31"',
        'type=artikel AND date within "1930-01-01 1939-12-31"',
        'type=artikel AND date within "1940-01-01 1941-12-31"',
    ]

    # END OF USER-SPECIFIC INPUTS

    # get number of available kb articles by decade
    # print("Available articles by decade:")
    # for query in queries:
    #     print(f"\t{query} : {get_jsru_match_count(query)}")

    # iterate over sample queries, and sample corresponding urls by decade
    for query in queries:

        print(f"\t{query} : {get_jsru_match_count(query)}")

        sav = "urls/" + query + ".txt"

        # ensure that output file path exists
        os.makedirs(os.path.dirname(sav), exist_ok=True)

        # pass if sav file already exists
        if os.path.exists(sav):
            pass
        else:
            urls: typing.Generator = pan_for_gold(
                query, split_width=split_width, n_splits=n_splits, per_split=per_split
            )

            with open(sav, "w") as f:
                lines = (url + "\n" for url in tqdm(urls, total=n_splits * per_split))
                f.writelines(lines)


def pan_for_gold(
    query: str, *, split_width: int, n_splits: int, per_split: int
) -> typing.Iterator:
    """Return a generator of random ocr urls matching a jsru query.

    To access the articles returned from a query, we must specify 'startRecord'
    and 'maximumRecords'. i.e., we are limited to returning a small snapshot only.

    This function samples the KB newspaper collection corresponding to a query,
    doing the following:
        * setting 'maximumRecords' to split_width: i.e., effectively breaking the
        pool into splits (pans).
        * randomly sample 'n_splits' of these splits.
        * from each split randomnly sample 'per_split' articles
    """

    # how large is our potential sampling pool?
    pool_size: int = get_jsru_match_count(query)
    assert split_width * n_splits <= pool_size, "sampled splits > available pool size"

    # conceptually, we imaging the pool in terms of splits of 'split_width'
    # get random startRecord values, analagous to randomly sampling splits
    random_split_starts = random.sample(range(1, pool_size, split_width), k=n_splits)

    base_url = (
        "http://jsru.kb.nl/sru/sru?version=1.2"
        + "&operation=searchRetrieve"
        + "&x-collection=DDD_artikel&"
        + "recordSchema=dc"
    )

    random_split_urls: typing.Iterator = (
        base_url
        + f"&startRecord={start}&maximumRecords={split_width}"
        + f"&query={(query)}"
        for start in random_split_starts
    )  # Iterator of urls to each randomly selected split

    random_splits: typing.Iterator = (
        (split_url, split)
        for split_url, split in gen_threaded(
            random_split_urls, f=get_page, chunk_size=50
        )
        if split is not None  # i.e., remove failed requests
    )  # iterator of (split_url, get_page(split_url))

    ocr_urls: typing.Iterator = itertools.chain.from_iterable(
        get_split_urls(split_url, split, per_split)
        for split_url, split in random_splits
    )  # iterator of urls (str) for all sampled random splits

    return ocr_urls


def get_split_urls(
    split_url: str, split: typing.Union[tuple, None], sample_size: int
) -> typing.Generator:
    """Return random sample of urls from a split of articles.

    Args:
        split_url: the jsru query url from which split is taken
        split: the output from get_page(split_url)
        sample_size (int): how many samples from split to randomnly sample.
    """

    for article in random.sample(split, k=sample_size):
        if pydash.objects.has(article, "srw:recordData.dc:identifier"):
            url: str = article["srw:recordData"]["dc:identifier"]
            yield url
        else:
            print(
                f"notice: could not retrieve url for article, {article}, in {split_url}"
            )


def get_page(url: str) -> typing.Union[tuple, None]:
    """Return the articles on a jsru page."""
    try:
        response = get_response(url, max_attempts=3, timeout=20)
        pan = xmltodict.parse(response.text)

        return pan["srw:searchRetrieveResponse"]["srw:records"]["srw:record"]

    except:
        print(f"could not fetch: {url}")
        return None


def get_jsru_match_count(query: str) -> int:
    """Return match count for query passed to http://jsru.kb.nl."""
    base_url = (
        "http://jsru.kb.nl/sru/sru?version=1.2"
        + "&operation=searchRetrieve"
        + "&x-collection=DDD_artikel&"
        + "recordSchema=dc"
    )

    r = get_response(base_url + "&startRecord=1&maximumRecords=1" + f"&query={(query)}")
    r: dict = xmltodict.parse(r.text)
    num_articles: int = int(r["srw:searchRetrieveResponse"]["srw:numberOfRecords"])

    return num_articles


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
        chunks = map(lambda i: iterable, range(1))  # chunks contains a single chunk

    for chunk in chunks:

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

            future_items = {executor.submit(f, item): item for item in chunk}

            for future in concurrent.futures.as_completed(future_items):
                yield (future_items[future], future.result())


def gen_chunks(iterable: typing.Iterable, chunk_size: int) -> typing.Generator:
    """Return a generator yielding chunks (as iterators) of passed iterable."""
    it = iter(iterable)
    while True:
        chunk = itertools.islice(it, chunk_size)
        try:
            first_el = next(chunk)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk)


def get_response(url: str, *, max_attempts=5, **request_kwargs) -> requests.Response:
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
