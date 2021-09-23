"""Profile the frequency of the text-analysed terms in the corpus.
"""
import typing
from collections import Counter

from tqdm import tqdm


def main():

    # get an iterator of text-analysed tokens
    sents: typing.Generator = gen_file_lines("embeddings/sents.txt")  # autostrips '\n'
    tokens_unrefined: typing.Iterator = (
        token for sent in sents for token in sent.split(" ")
    )
    tokens: typing.Iterator = (
        token for token in tokens_unrefined if token != ""
    )  # remove '' tokens

    # compile frequencies
    frequencies = Counter(tokens)
    print(len(frequencies.keys()))


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
