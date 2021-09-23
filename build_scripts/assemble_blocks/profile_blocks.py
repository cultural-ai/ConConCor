"""
Double check the number of contentious, alternative, additional and control extracts in each block.
"""

import csv
import typing
from collections import Counter


def main():

    # ------
    # get counts of p, n, a and c in each block of 50
    # ------
    records = [["block", "n_count", "p_count", "c_count", "a_count"]]
    block_record = [0, 0, 0, 0, 0]
    for index, row in enumerate(gen_csv_rows("blocks.csv", ignore_rows=[0]), start=1):

        row_class = row[4]
        if row_class == "n":
            block_record[1] += 1
        elif row_class == "p":
            block_record[2] += 1
        elif row_class == "c":
            block_record[3] += 1
        elif row_class == "a":
            block_record[4] += 1

        if index // 50 != block_record[0]:
            records.append(block_record)
            block_record = [index // 50, 0, 0, 0, 0]

    with open("profile_blocks.csv", "w") as f:
        write = csv.writer(f)
        write.writerows(records)

    # ------
    # whats the word coverage like in each of our streams?
    # ------

    matches_p = Counter()
    matches_n = Counter()

    for index, row in enumerate(gen_csv_rows("blocks.csv", ignore_rows=[0])):

        query = row[2]
        row_class = row[4]  # i.e.,  'p', 'n', 'a', 'c'

        if row_class == 'p':
            matches_p[query] += 1
        elif row_class == 'n':
            matches_n[query] += 1

    with open("profile_blocks_matching_n.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(['query word', 'count'])
        for query, count in dict(matches_n).items():
            writer.writerow([query, count])

    with open("profile_blocks_matching_p.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(['query word', 'count'])
        for query, count in dict(matches_p).items():
            writer.writerow([query, count])


def gen_csv_rows(path: str, *, ignore_rows: typing.List = []):
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


if __name__ == "__main__":
    main()
