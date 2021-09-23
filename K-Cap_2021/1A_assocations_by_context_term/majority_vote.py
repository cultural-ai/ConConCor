"""
Return a dataframe of | extract_id | label |
where label is 1, 0 (or 0.5 if no majority) as decided by majority vote

process:
* load data (with control samples/annotations removed);
* remove 'week ik niet' and 'onleesbare' annotations;
* assign label based on proportion of remaining annotations by sample have 
"""

import pandas as pd
import os


def main():

    with open("data.csv", "r") as f:
        data = pd.read_csv(f)

    # keep only contentious/non-contentious responses
    data = data[
        data["response"].isin(["Omstreden naar huidige maatstaven", "Niet omstreden"])
    ]
    # case fold 'target_compound'
    data["target_compound"] = data["target_compound"].str.lower()

    # label as 1 (contentious) or 0 based on majority vote by extract_id
    data["label"] = data["response"].apply(
        lambda x: 1 if x == "Omstreden naar huidige maatstaven" else 0
    )
    grouped: pd.DataFrame = data.groupby(["extract_id"]).mean()
    grouped["label"] = grouped["label"].apply(majority_vote)

    # print info
    print(f'{grouped.shape[0]} extract ids')
    print(f'{grouped[grouped["label"]==1].shape[0]} contentious')
    print(f'{grouped[grouped["label"]==0].shape[0]} non-contentious')
    print(f'{grouped[grouped["label"]==0.5].shape[0]} no overall majority')

    sav_file = 'majority_vote/majority_vote.csv'
    os.makedirs(os.path.dirname(sav_file), exist_ok=True)
    with open(sav_file, 'w') as f:
        grouped.to_csv(f)


def majority_vote(proportion: float) -> float:
    """Get the majority vote."""
    if proportion == 0.5:
        return 0.5
    elif proportion > 0.5:
        return 1
    else:
        return 0


if __name__ == "__main__":
    main()
