"""How well do our embeddings capture our annotation set vocabulary?
"""

import json
from functools import partial

import numpy as np
import pandas as pd
from gensim.models import Word2Vec


def main():

    # embeddings subset tokens
    with open("embeddings_subset/tokens.json", "r") as f:
        tokens_subset: set = set(json.load(f))

    # get the larger pool of embeddings
    model = Word2Vec.load("embeddings/w2v.model")
    tokens_larger: set = set(
        model.wv.key_to_index
    )  # i.e., tokens[0] is the token corresponding to X[0]

    # get the annotations
    with open("data.csv", "r") as f:
        data = pd.read_csv(f)

    # find the matched, ...
    data = data.apply(partial(compare, vocabulary=tokens_subset, col_prefix='em_subset'), axis=1)
    data = data.apply(partial(compare, vocabulary=tokens_larger, col_prefix='em_larger'), axis=1)

    # stats
    print(f"tokens subset length:{len(tokens_subset)}")
    print(f"tokens full length:{len(tokens_larger)}")

    with open('inspect.csv', 'w') as f:
        data.to_csv(f)


def compare(row, *, vocabulary: set, col_prefix: str) -> tuple:
    """Return row with known and unknown tokens in 'text_analysed'"""

    text = row["text_analysed"]

    # collect the known, unknown tokens in 'text'
    known = set()
    unknown = set()
    for sent in text.split("<sent>"):
        for token in sent.split(" "):
            if token != "" and token != " ":
                if token in vocabulary:
                    known.add(token)
                else:
                    unknown.add(token)

    # append to row
    row[col_prefix + "_known"] = ", ".join(known)
    row[col_prefix + "_unknown"] = ", ".join(unknown)
    row[col_prefix + "%_known"] = len(known) / (len(known) + len(unknown))

    return row


if __name__ == "__main__":
    main()
