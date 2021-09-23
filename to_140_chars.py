"""Amend the samples in Extracts.csv to max 140 characters.
"""
import re
from math import floor

import pandas as pd


def main():

    # replace extracts.text with a shortened version
    extracts: pd.DataFrame = pd.read_csv("Extracts.csv")
    extracts["text"] = extracts.apply(shorten_chars, axis=1)

    with open("Extracts_amended.csv", "w") as f:
        extracts.to_csv(f)


def shorten_chars(row):
    """Return <= 140 chars around the target word."""

    text: str = row["text"].replace('\n','')

    target: str = row["target_compound_bolded"]

    target_index: int = text.index(target)

    side_capture_length: int = floor(
        (140 - len(target)) / 2
    )  # number of chars either of the token to match

    matched: str = text[
        max(0, target_index - side_capture_length) : min(
            len(text), target_index + len(target) + side_capture_length
        )
    ] 

    return matched


if __name__ == "__main__":
    main()
