"""
Calculate various stats regarding how associated a context token is with contentiousness.

Output: stats/stats_{depth}.csv

Process:
    * load the annotation set (controls already removed):
        * remove 'Weet ik niet' and 'Onleesbare...' annotations
        * case-fold target words 
    * With respect to the text-analysed context tokens
        * build a hash of {context cluster|str| : co-occurrent extract ids|set|, ...}
        * build a hash of {context cluster|str| : Counter{target1: 2, target2:1,... }, ...}
    * build and save a dataframe with:
        * e.g., ratios of count(cluster, contentious) / count(cluster), binomial test
          such to measure significance wrt., contentious sample or
          non-contentious sample association
"""

import json
import os
import re
import typing
from collections import Counter, defaultdict

import pandas as pd
from scipy.stats import binom_test


def main():

    # ------
    # load data
    # ------
    with open("data.csv", "r") as f:
        data = pd.read_csv(f)

    # remove all 'weet ik niet' and 'Onleesbare ...'
    data = data[
        data["response"].isin(["Omstreden naar huidige maatstaven", "Niet omstreden"])
    ]

    # case fold target_compound
    data["target_compound"] = data["target_compound"].str.lower()

    # get a series of text-analysed contexts by extract_id
    contexts: pd.Series = data.groupby(["extract_id"]).first().loc[:, "text_analysed"]

    # ------
    # load dataframe of | extract_id | label |
    # ------
    with open("majority_vote/majority_vote.csv", "r") as f:
        majority_vote = pd.read_csv(f)
    majority_vote = majority_vote.set_index("extract_id")

    # ------
    # Iterate over cluster hashes
    # ------

    # consider each cluster hash in-turn
    hashes = gen_dir("cluster_hashes", pattern=r"\.*.json")
    for h_path in hashes:  # iterate of hash file paths

        depth = re.search(r"[0-9]+", h_path).group(0)

        # load the hash
        with open("cluster_hashes/" + h_path, "r") as f:
            h = json.load(f)


        # ------
        # Construct extract id associations with cluster, and cluster's respective tokens
        # ------

        # build extracts_by_context_cluster = {cluster:set of extract ids, }
        extracts_by_context_cluster = defaultdict(set)
        flagged_contexts_by_cluster = defaultdict(Counter)
        for extract_id, text in contexts.iteritems():

            # iterate over context tokens
            seen_terms = set()
            for context_token in set(
                [
                    t
                    for s in text.split("<sent>")
                    for t in s.split(" ")
                    if t != "" and t != " "
                ]
            ):
                # record extract_id against context_token's parent cluster
                # (only once)
                if context_token in h and context_token not in seen_terms:
                    cluster = h[context_token]
                    extracts_by_context_cluster[cluster].add(extract_id) 

                    # how many times a clusters' context tokens appear in the extracts
                    flagged_contexts_by_cluster[cluster][context_token] += 1

        # build target_words_by_context_cluster = {cluster: list of associated target words}
        target_words_by_id = (
            data.groupby(["extract_id"]).first().loc[:, "target_compound"]
        )

        target_words_by_context_cluster = defaultdict(Counter)
        for cluster, extract_ids in extracts_by_context_cluster.items():
            for extract_id in extract_ids:
                target = target_words_by_id.at[extract_id]
                target_words_by_context_cluster[cluster][target] += 1

        # ------
        # build df of statistics
        # ------
        stats = defaultdict(list)
        for cluster, extract_ids in extracts_by_context_cluster.items():

            votes = [
                majority_vote.at[extract_id, "label"] for extract_id in extract_ids
            ]  # votes associated with all context clusters
            stats["cluster"].append(cluster)
            stats["num_corresponding_extracts"].append(len(votes))

            count_c = sum([1 for v in votes if v == 1])
            count_n = sum([1 for v in votes if v == 0])
            count_u = sum([1 for v in votes if v == 0.5])
            count = len(votes)

            # attribute point estimates and p-values
            stats["proportion_with_contentious"].append((count_c) / (count))
            stats["contentious_p_value"].append(
                binom_test(count_c, count, p=0.183, alternative="greater")
            )
            stats["proportion_with_non_contentious"].append((count_n) / (count))
            stats["non_contentious_p_value"].append(
                binom_test(count_n, count, p=0.796, alternative="greater")
            )
            stats["proportion_with_no_majority"].append((count_u) / (count))

            # attibute number of target words and number of instances
            targets = target_words_by_context_cluster[cluster]
            target_string = ", ".join(
                [t + f"({count})" for t, count in targets.items()]
            )
            stats["targets_count"].append(sum([1 for t, c in targets.items()]))
            stats["targets"].append(target_string)

            # attibute distribution of context words
            stats["context_tokens_occuring"].append(
                ", ".join(
                    [str(c) for c in flagged_contexts_by_cluster[cluster].items()]
                )
            )

            # context words - for cut and paste translate
            stats["context_tokens_occuring2"].append(
                ", ".join([i for i, j in flagged_contexts_by_cluster[cluster].items()])
            )

        # save as a dataframe
        stats = pd.DataFrame.from_dict(stats)
        sav = f"stats/stats_{depth}.csv"
        os.makedirs(os.path.dirname(sav), exist_ok=True)
        with open(sav, "w") as f:
            stats.to_csv(f)


def gen_dir(dir: str = os.getcwd(), *, pattern: str = ".+") -> typing.Generator:
    """Return a generator of absolute paths of file in a directory, optionally matching a pattern.

    Args:
        dir (str): [default: script dir]
        pattern (str): filename pattern to match against [default: any file]
    """

    for filename in os.listdir(dir):
        if re.search(pattern, filename):
            yield filename
        else:
            continue


if __name__ == "__main__":
    main()
