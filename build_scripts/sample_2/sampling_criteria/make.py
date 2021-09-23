"""
Make the queries (word + date) used by sample.py

Requires: Contentious.txt, Alternative.txt, Additional.txt, dates_artikel.txt
Out: Contentious_with_dates.txt, Alternative_with_dates.txt, Additional_with_dates.txt
"""

import itertools
import typing


def main():

    # queries to join:tuple, and what to call output file
    contentious_info = [
        (
            "../../sample_1/queries/Contentious.txt",
            "../../sample_1/queries/dates_artikel.txt",
        ),
        "contentious_criteria.txt",  # output file name
    ]
    alternative_info = [
        (
            "../../sample_1/queries/Alternative.txt",
            "../../sample_1/queries/dates_artikel.txt",
        ),
        "alternative_criteria.txt",  # output file name
    ]
    additional_info = [
        (
            "../../sample_1/queries/Additional.txt",
            "../../sample_1/queries/dates_artikel.txt",
        ),
        "additional_criteria.txt",  # output file name
    ]

    for query_pair, sav_name in [contentious_info, alternative_info, additional_info]:

        # get list of query combinations
        query_combinations = []
        for combination_tuple in gen_file_lines_combinations(query_pair):
            query = " AND ".join(combination_tuple)
            query_combinations.append(query)

        # output list to file
        with open(sav_name, "w") as f:
            f.writelines([query + "\n" for query in query_combinations])


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
