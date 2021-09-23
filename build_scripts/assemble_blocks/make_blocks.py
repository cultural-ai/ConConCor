""" Generate 60 sheets of 50 samples.
    20:20:5:5 ; positive:negative:additional:control

run
```
python3.py make_blocks.py
```

Requires:
    * 
"""


import csv
import random
import typing
from copy import copy

import pandas as pd


def main():

    # ------
    # import the sampled extracts
    # ------
    negative = gen_csv_rows(
        "../sample_2/alternative_words/sampled.csv", ignore_rows=[0]
    )

    positive = gen_csv_rows(
        "../sample_2/contentious_words/sampled.csv", ignore_rows=[0]
    )

    additional = gen_csv_rows(
        "../sample_2/additional_words/sampled.csv", ignore_rows=[0]
    )

    control = list(gen_csv_rows("control.csv", ignore_rows=[0]))

    huc = list(
        gen_csv_rows("huc_study.csv", ignore_rows=[0])
    )  # extracts used in previous study

    # ------
    # the csv files are pre-shuffled ...
    # we just pull our results in order ... to each form
    # ------

    # keep counters of each type
    counter_n = 0
    counter_p = 0
    counter_a = 0

    collected: typing.List = [["", "url", "query", "extract"]]

    for i in range(60):

        # create new list and append control
        temp: list = []
        temp += [c + ["c"] for c in control]
        print(temp)
        exit(1)

        # add next 20 negative not previously seen in temp or huc
        counter = 0
        while counter < 20:
            potential = next(negative)
            counter_n += 1
            if potential not in temp and potential not in huc:
                temp.append(potential + ["n"])
                counter += 1

        # add next 10 positive not previously seen in temp or huc
        counter = 0
        while counter < 20:
            potential = next(positive)
            counter_p += 1
            if potential not in temp and potential not in huc:
                temp.append(potential + ["p"])
                counter += 1

        # add next 10 additional not previously seen in temp or huc
        counter = 0
        while counter < 5:
            potential = next(additional)
            counter_a += 1
            if potential not in temp and potential not in huc:
                temp.append(potential + ["a"])
                counter += 1

        # randomly shuffle this
        random.shuffle(temp)
        collected += temp

    print(f"{counter_n} negative extracts considered")
    print(f"{counter_p} positive extracts considered")
    print(f"{counter_a} additional extracts considered")

    with open("blocks.csv", "w") as f:
        write = csv.writer(f)
        write.writerows(collected)


def gen_csv_rows(path: str, *, ignore_rows: list = []) -> typing.Generator:
    """Return a generator yielding successive csv rows.

    Will ignore row indices specified in ignore_rows arg.

    Args:
        path (str): path to csv
        ignore_rows (list): E.g., title row = [0]
    """
    with open(path, "r") as f:
        for index, line in enumerate(csv.reader(f)):
            if index not in ignore_rows:
                yield line


def max_index(input: typing.List) -> int:
    return len(input) - 1


if __name__ == "__main__":
    main()
