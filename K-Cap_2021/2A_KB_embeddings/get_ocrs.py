"""
Retrieve ocr files corresponding to the urls sampled in urls/
store in ocrs/
"""
import typing
import concurrent.futures
import re
import requests
import os
import time
import itertools
import xmltodict
from tqdm import tqdm


def main():

    # iterate over url files and extract ocrs for corresponding urls
    urls_filenames = gen_dir("urls", pattern=".*\.txt$")
    for urls_filename in urls_filenames:

        print(f"retrieve ocr files ")

        urls = gen_file_lines(
            "urls/" + urls_filename
        )  # generator of urls contained in urls_filename

        ocrs: typing.Iterator = (
            (url, ocr)
            for url, ocr in gen_threaded(urls, f=get_ocr, chunk_size=100)
            if ocr is not None  # remove failed get_ocr calls (or otherwise empty ocr files)
        )  # iterator of (url:str, paragraphs:list) for each ocr file

        sav = f"ocrs/{urls_filename}"
        os.makedirs(os.path.dirname(sav), exist_ok=True)  # ensure sav dirs

        # pass if sav exists
        if os.path.exists(sav):
            pass
        else:
            lines = (
                f"<ocr url={url}>" + "<par>".join(paragraphs) + "</ocr>" + "\n"
                for url, paragraphs in tqdm(ocrs, total=10000)
            )

            with open(sav, "w") as f:
                f.writelines(lines)


def get_ocr(url: str) -> typing.Union[list, None]:
    """Returns a list of paragraphs from an OCR file.

    Returns None if no paragraphs, or if request fails.
    """
    try:
        response = get_response(url)
        ocr: dict = xmltodict.parse(response.text)
        p = ocr["text"]["p"]

        # multi-paragraph-containing ocr files, apparently hold their paragraphs
        # in a list, and single-paragraph-containing ocr files don't
        if isinstance(p, list):
            return p
        elif p is None:
            # paragraph empty, e.g.,
            # http://resolver.kb.nl/resolve?urn=ddd:010590956:mpeg21:a0033:ocr
            return None
        else:
            return [p]
    except:
        print(f"failed to fetch: {url}")
        return None  # failed


def gen_dir(dir: str = os.getcwd(), *, pattern: str = ".+") -> typing.Generator:
    """Return a generator yielding filenames in a directory, optionally matching a pattern.

    Args:
        dir (str): [default: script dir]
        pattern (str): filename pattern to match against [default: any file]
    """

    for filename in os.listdir(dir):
        if re.search(pattern, filename):
            yield filename
        else:
            continue


def gen_file_lines(path: str, *, strip="\n", apply=None) -> typing.Generator:
    """Return a generator yielding successive file lines.

    Args:
        path (str): path to txt file
        strip (str): string to strip from lines, by default '\n'
        apply (callable): apply a function to the string after 'strip' applied.
    """
    with open(path, "r") as f:
        for line in f:
            if apply:
                yield apply(line.strip(strip))
            else:
                yield line.strip(strip)


def get_response(url: str, *, max_attempts=5) -> requests.Response:
    """Return the response.

    Tries to get response max_attempts number of times, otherwise return None

    Args:
       url (str): url string to be retrieved
       max_attemps (int): number of request attempts for same url

    E.g.,
        r = get_response(url)
        r = xmltodict.parse(r.text)
        # or
        r = json.load(r.text)
    """
    for count, x in enumerate(range(max_attempts)):
        try:
            response = requests.get(url, timeout=10)
            return response
        except:
            time.sleep(0.01)

    # if count exceeded
    return None


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


def gen_map(iterable: typing.Iterable, *, f: typing.Callable) -> typing.Generator:
    """Return a generator yielding tuple (item, f(item)).

    Example:
        g = gen_map(urls, get_response)
        url, response = next(g)
    """
    for i in iterable:
        yield (i, f(i))


if __name__ == "__main__":
    main()
