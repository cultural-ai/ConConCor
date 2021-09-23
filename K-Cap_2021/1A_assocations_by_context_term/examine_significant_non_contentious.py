"""
Gate a table of 20 context terms with highest P(contentious|token), 
"""
from collections import defaultdict

import pandas as pd


def main():

    with open("stats/p_response_given_context.csv", "r") as f:
        stats = pd.read_csv(f)

    # Consider a range of min 'targets_count' wrt., a context word
    d = defaultdict(list)
    for min_targets_count in [0, 10, 20, 50]:

        # get only stats of significant tokens
        stats_of_interest = stats.loc[
            (stats["targets_count"] >= min_targets_count) & (stats["non_contentious_p_value"] < 0.05),
            :,
        ].sort_values("p_non_given_context_token", ascending=False)

        # create a string of "token (0.76), token(0.65), ..."
        entries = []
        for count, (index, row) in enumerate(stats_of_interest.iloc[:20, :].iterrows()):
            # entries.append(f"{row['token']}({row['p_non_given_context_token']:.2f})")
            entries.append(f"{row['token']}")

        d["min target count"].append(str(min_targets_count))
        d["tokens significantly associated with contentious samples"].append(
            ", ".join(entries)
        )

    # sav
    df = pd.DataFrame.from_dict(d)
    with open("non_contentious_terms_various_t.csv", "w") as f:
        df.to_csv(f)


if __name__ == "__main__":
    main()
