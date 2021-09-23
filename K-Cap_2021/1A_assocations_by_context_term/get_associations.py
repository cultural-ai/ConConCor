"""
Calculate various stats regarding how associated a context token is with contentiousness.
process:
    * load the annotation set (controls already removed):
        * remove 'weet ik niet' and 'Onleesbare...' annotations
        * case-fold target words 
    * With respect to the text-analysed context tokens
        * build a hash of {context token|str| : co-occurrent extract ids|set|, ...}
        * build a hash of {context token|str| : Counter{target1: 2, target2:1,... }, ...}
    * build and save a dataframe with:
        * e.g., ratios of count(token, contentious) / count(token), binomial test
          such to measure significance wrt., contentious sample or
          non-contentious sample association
"""

import os
from collections import Counter, defaultdict

import pandas as pd
from scipy.stats import binom_test
from statsmodels.stats.proportion import proportion_confint
from tqdm import tqdm


def main():

    sav = "stats/associations.csv"
    os.makedirs(os.path.dirname(sav), exist_ok=True)

    # pass of sav exists
    if os.path.exists(sav):
        pass
    else:

        # load data
        with open("data.csv", "r") as f:
            data = pd.read_csv(f)

        # remove all 'weet ik niet' and 'Onleesbare ...'
        data = data[
            data["response"].isin(
                ["Omstreden naar huidige maatstaven", "Niet omstreden"]
            )
        ]

        # case fold target_compound
        data['target_compound'] = data['target_compound'].str.lower()

        # get a series of text-analysed contexts by extract_id
        contexts: pd.Series = (
            data.groupby(["extract_id"]).first().loc[:, "text_analysed"]
        )

        # load dataframe of | extract_id | label |
        with open("majority_vote/majority_vote.csv", "r") as f:
            majority_vote = pd.read_csv(f)
        majority_vote = majority_vote.set_index("extract_id")

        # build {context token: list of extract_ids}
        extracts_by_context_token = defaultdict(list)
        for extract_id, text in contexts.iteritems():
            for context_token in set(
                [
                    t
                    for s in text.split("<sent>")
                    for t in s.split(" ")
                    if t != "" and t != " "
                ]
            ):
                extracts_by_context_token[context_token].append(extract_id)

        # build {context token: list of associated target words}
        target_words_by_id = (
            data.groupby(["extract_id"]).first().loc[:, "target_compound"]
        )

        target_words_by_context_token = defaultdict(Counter)  #
        for context_token, extract_ids in extracts_by_context_token.items():
            for extract_id in extract_ids:
                target = target_words_by_id.at[extract_id]
                target_words_by_context_token[context_token][target] += 1

        # ------
        # build df of statistics
        # ------
        stats = defaultdict(list)
        for context_token, extract_ids in extracts_by_context_token.items():

            votes = [
                majority_vote.at[extract_id, "label"] for extract_id in extract_ids
            ]
            stats["token"].append(context_token)
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
            targets = target_words_by_context_token[context_token]
            target_string = ", ".join(
                [t + f"({count})" for t, count in targets.items()]
            )
            stats['targets_count'].append(sum([1 for t, c in targets.items()]))
            stats["targets"].append(target_string)

        # save as a dataframe
        stats = pd.DataFrame.from_dict(stats)
        os.makedirs(os.path.dirname(sav), exist_ok=True)
        with open(sav, "w") as f:
            stats.to_csv(f)


if __name__ == "__main__":
    main()
