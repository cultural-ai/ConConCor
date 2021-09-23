import json
import typing
from collections import Counter
import os


def main():

    # output file
    sav_keep = "embeddings/keep_tokens.json"

    # pass if sav_keep exists
    if os.path.exists(sav_keep):
        pass
    else:
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

        # get a list of words to be removed from embeddings
        keep_tokens = [token for token, freq in frequencies.items() if freq >= 20]
        # print(len(keep_tokens))
        with open(sav_keep, "w") as f:
            json.dump(keep_tokens, f)


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
