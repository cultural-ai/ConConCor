""" Consolidate Annotations.csv, Extracts.csv, Metadata.csv, Demographics.csv into a single dataframe.

Note: get_nlp() and text_analysis() are identical to functions of the same name in ../CCC_embeddings/text_analysis.py
"""

import itertools
import os
import re
import typing
from functools import partial

import pandas as pd
import spacy


def main():

    sav = "data.csv"
    if os.path.exists(sav):  # don't overwrite an existing data.csv
        pass
    else:

        #
        # load in the datasheets
        #

        with open(os.path.dirname(__file__) + "/Annotations.csv") as f:
            annotations: pd.DataFrame = pd.read_csv(f)
        print(
            f'number of annotators: {len(set(annotations["anonymised_participant_id"]))}'
        )

        # with open('dataset/Demographics.csv') as f:
        #     demographics: pd.DataFrame = pd.read_csv(f)

        with open(os.path.dirname(__file__) + "/Extracts.csv") as f:
            extracts: pd.DataFrame = pd.read_csv(f)

        with open(os.path.dirname(__file__) + "/Metadata.csv") as f:
            metadata: pd.DataFrame = pd.read_csv(f)

        print("merging the data sheets")

        annotations = annotations.loc[:, ["extract_id", "response"]]
        annotations.set_index("extract_id")

        # join modified annotations with extracts
        joined = pd.merge(annotations, extracts, how="left", on="extract_id")

        # join  modified annotaitons, extracts with metadata
        joined = pd.merge(joined, metadata, how="left", on="url")
        print(f"number of annotations prior to removing controls: {joined.shape}")

        # remove the control examples:
        joined = joined[
            joined["extract_id"].isin(["c0", "c1", "c2", "c3", "c4"]) == False
        ]
        print(f"number of annotations after removing controls: {joined.shape}")

        #
        # perform text-analysis on the annotation contexts
        #
        print('creating column "text_analysed"')
        nlp = get_nlp()

        joined["text_analysed"]: pd.Series = joined.apply(
            lambda row: row["text"].replace(row["target_compound_bolded"], ""), axis=1
        )  # create a new series, removing the target word

        joined["text_analysed"] = joined.apply(
            lambda row: text_analysis(row["text_analysed"], nlp=nlp), axis=1
        )  # apply the same text-analysis as the embedding training corpus

        #
        # save
        #
        with open(sav, "w") as f:
            # annotations.to_csv(f)
            joined.to_csv(f, index=False)


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
        tokens = ["<NUMERIC>" if contains_numeric(token) else token for token in tokens]

        sents.append(" ".join(tokens))

    return "<sent>".join(sents)


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


def contains_numeric(text: str) -> bool:
    if re.search('[0-9]+', text):
        return True
    else:
        return False

if __name__ == "__main__":
    main()
