"""
P(response|context cluster presence) for a given sample, based on sample
majority vote scores.
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
    # cluster of interest: to be iterated over and determine significance
    # = {'label'|str|:(hash_level|int| : set of context tokens|list|}
    # ! ENSURE A TOKENS ARE UNIQUE TO LABELS
    # ------
    sav_suffix = "religion_15_341825"
    clusters_of_interest = {'religion_8_341825':(8, set(["joden", "niet-christen", "profeet", "romein", "christen", "evangelie", "christus", "dienaar", "gods", "sect", "god", "ood",  "huwen", "allah", "voorvader", "bedienaar", "heilig", "boeddhistisch", "roemrijk", "woord", "heere", "bidden", "heilige", "geloofsgenoot", "troost", "geloofs", "medebroeder", "herder", "bewonderaar", "vaderlandsch", "geslacht", "goddelijk", "jezus", "adelijk", "brochure", "zegen", "gesneuvelde", "profetie", "nakomeling", "avontuurlijk", "heiligheid", "zalig", "godheid", "apostel", "genesis", "joodsch", "kruises", "confessie", "legende", "offerande", "afkomst", "kruise", "heerlijkheid", "gode", "belijden", "edele", "mythe", "kindor", "martelaar", "geloovlg", "heiden", "iong", "zegenen", "bekeering", "voorzienigheid", "secte", "zaligheid", "levenslicht", "belijdenis", "roemvol", "gevallene", "babel", "rechterstoel", "zondaar", "jongo", "almachtig", "voorouder", "zionisme", "triomf", "bijbelverhaal", "jesus", "gebod", "romeinen", "calvijn", "eerbiedig", "berinnering", "stervende", "bladzijde", "exodus", "valkenjacht", "weldoenster", "avontuur", "ziekbed", "belijder", "smeeken", "buddha", "bedroefd", "beminnen", "loovig", "andersdenkend", "geliefd", "salomo", "joodsche", "viouw", "godsrijk", "hemelschen", "missieland", "nageslacht", "allerhoogste", "roemruchtig", "legendarisch", "toovenaar", "heiligen", "grondvester", "marteldood", "fabel", "afkorten", "triomfantelijk", "stervensuur", "weldoener", "geloofsbelijdenis", "pupil", "juffer", "engel", "nakomelingschap", "apostelen", "bidd", "overlevering", "nari", "zion", "rabbi", "heiland", "baby", "gelovig", "rouwen", "zegening", "heidenen", "triomfator", "oods", "voorgeslacht", "heks", "farao", "zielenheil", "wederkomst", "verlosser", "goden", "grafschrift", "lauwer", "thora", "joods", "vereering", "troostwoord", "discipel", "sinai" ]))} 

    # convert to hash of {'token':'label', }
    h = {token:label for label, (hash_level, s) in clusters_of_interest.items() for token in s}

    # ------
    # load data
    # ------
    with open("../data.csv", "r") as f:
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
    with open("../majority_vote/majority_vote.csv", "r") as f:
        majority_vote = pd.read_csv(f)
    majority_vote = majority_vote.set_index("extract_id")


    # ------
    # Construct extract id associations with cluster, and cluster's respective tokens
    # ------
    extracts_by_cluster = defaultdict(set)  # cluster_label|str| : set of extract ids present|list|
    flagged_contexts_by_cluster = defaultdict(Counter)  # cluster_label|str| : Counter({context_tokens: count of unique extract appears in})
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

            # add unseen terms (wrt., current extract) present in hashes to ...
            if context_token in h and context_token not in seen_terms:
                seen_terms.add(context_token)

                cluster_label = h[context_token]
                extracts_by_cluster[cluster_label].add(extract_id)  # each extract only associated once with an extract regardless of frequency

                # how many extracts a clusters' context tokens appears
                flagged_contexts_by_cluster[cluster_label][context_token] += 1

    # build target_words_by_context_cluster = {cluster_label|str|: associated target words|list|}
    target_words_by_id = (
        data.groupby(["extract_id"]).first().loc[:, "target_compound"]
    )

    target_words_by_context_cluster = defaultdict(Counter)
    for cluster_label, extract_ids in extracts_by_cluster.items():
        for extract_id in extract_ids:
            target = target_words_by_id.at[extract_id]
            target_words_by_context_cluster[cluster_label][target] += 1


    # ------
    # build df of statistics wrt., selected clusters
    # ------
    stats = defaultdict(list)
    for cluster_label, extract_ids in extracts_by_cluster.items():

        votes = [
            majority_vote.at[extract_id, "label"] for extract_id in extract_ids
        ]  # votes associated with all context clusters
        stats["cluster"].append(cluster_label)
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
        stats["proportion_with_no_majority"].append(
            binom_test(count_n, count, p=0.796, alternative="greater")
        )
        stats["p_no_maj_given_context_cluster"].append((count_u) / (count))

        # attibute number of target words and number of instances
        targets = target_words_by_context_cluster[cluster_label]
        target_string = ", ".join(
            [t + f"({count})" for t, count in targets.items()]
        )
        stats["targets_count"].append(sum([1 for t, c in targets.items()]))
        stats["targets"].append(target_string)

        # attibute distribution of context words
        stats["context_tokens_occuring"].append(
            ", ".join(
                [str(c) for c in flagged_contexts_by_cluster[cluster_label].items()]
            )
        )

        # context words - for cut and paste translate
        stats["context_tokens_occuring2"].append(
            ", ".join([i for i, j in flagged_contexts_by_cluster[cluster_label].items()])
        )

        # save as a dataframe
        stats = pd.DataFrame.from_dict(stats)
        sav = f"selected/stats_{sav_suffix}.csv"
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
