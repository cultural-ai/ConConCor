"""
Perform text analysis on the DL'd ocr files in ocrs/
store text_analysed ocrs in /text_analysis

Note: post-processed articles are stored between <ocr .*?>|</ocr> tags, with
sentences separated by <sent> unitags
"""
import itertools
import os
import re
import typing
from functools import partial
from multiprocessing import Pool
from itertools import chain

import spacy


def main():

    #
    # setup spaCy
    #
    print("setting up spacy")
    nlp = get_nlp()

    #
    # perform text analysis of ocrs
    #
    ocrs_filenames: typing.Generator = gen_dir("ocrs", pattern=".*\.txt$")
    for ocrs_filename in ocrs_filenames:

        # save
        sav = f"text_analysis/{ocrs_filename}"
        os.makedirs(os.path.dirname(sav), exist_ok=True)  # ensure sav dirs

        # pass if sav already exists
        if os.path.exists(sav):
            pass
        else:

            ocrs_filepath = "ocrs/" + ocrs_filename

            print(f"performing text analysis on {ocrs_filepath}")

            ocrs: typing.Generator = gen_file_lines(
                ocrs_filepath
            )  # generator of <ocr></ocr> files, for a  single file in ocrs/

            pool = Pool()
            analysed_ocrs = pool.imap(
                partial(analyse_ocr, nlp=nlp), ocrs, chunksize=100
            )  # iterator of post-text analysis versions of ocr files, maintaining tags

            with open(sav, "w") as f:
                lines = (ocr + "\n" for ocr in analysed_ocrs)
                f.writelines(lines)


def analyse_ocr(ocr: str, nlp) -> str:
    """Return a text-analysed version of ocr.

    Args:
        ocr (str): a <ocr .*></ocr> bounded string of a single ocr record.
    """

    # remove the opening and closing tags
    open_tag, text, close_tag = (
        split for split in re.split(r"(<ocr .*?>|</ocr>)", ocr) if split != ""
    )

    paragraphs = text.split("<par>")  # list of paragraphs

    analysed_paragraphs: typing.Iterator = map(
        partial(text_analysis, nlp=nlp), paragraphs
    )  # iterator paragraph: str

    return open_tag + "<par>".join(analysed_paragraphs) + close_tag


def text_analysis(string: str, *, nlp) -> str:
    """Return a text analysed string.

    post-analysis sentences are separated by <sent> tags
    e.g., 'a sentence<sent>a second sentence<sent>a third.

    see https://spacy.io/usage/rule-based-matching#adding-patterns-attributes
    """
    sents = []

    doc = nlp(string)
    for sent in doc.sents:

        tokens = [token for token in sent if len(token) >= 3]

        # remove puntuation
        tokens = [token for token in tokens if token.is_punct == False]


        # remove stop words
        tokens = [token for token in tokens if not token.is_stop]

        # lemmatize
        tokens = [token.lemma_ for token in tokens]

        # convert numeric to '<NUMERIC>'
        tokens = ['<NUMERIC>' if contains_numeric(token) else token for token in tokens]

        sents.append(" ".join(tokens))
        
    return "<sent>".join(sents)


def contains_numeric(text: str) -> bool:
    if re.search('[0-9]+', text):
        return True
    else:
        return False

def get_nlp():
    """Return a configured 'nlp' object."""
    nlp = spacy.load("nl_core_news_sm")

    # don't need syntactic parsing - senter is faster
    nlp.disable_pipe("parser")
    nlp.enable_pipe("senter")

    # use lookup based lemmatizer
    # nlp.remove_pipe("lemmatizer")
    # nlp.add_pipe("lemmatizer", config={"mode": "lookup"}).initialize()

    return nlp


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


def gen_file_lines(path: str, *, strip: list = ["\n"]) -> typing.Generator:
    """Return a generator yielding successive file lines.

    Args:
        path (str): path to txt file
        strip (list): a list of callables to be recursively applied to each line

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


if __name__ == "__main__":
    main()
