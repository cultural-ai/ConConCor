import argparse
import json
import pickle as pkl

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-c", nargs=1, type=int)


def main():

    args = parser.parse_args()

    # load the linkage matrix
    sav_linkages = "heirarchical_clustering/linkage_matrix.pkl"
    with open(sav_linkages, "rb") as f:
        z: np.ndarray = pkl.load(f)

    # sav_tokens = "heirarchical_clustering/tokens.json"
    sav_tokens = "heirarchical_clustering/tokens.json"
    with open(sav_tokens, "rb") as f:
        tokens: list = json.load(f)

    print(", ".join(cluster_index_to_tokens(args.c[0], z=z, tokens=tokens)))


def cluster_index_to_tokens(cluster_index: int, *, z: np.ndarray, tokens: list) -> list:
    """Return a list of tokens corresponding to a cluster index (as per z[:, 0:2]) values."""

    if cluster_index < len(tokens):
        return [tokens[cluster_index]]
    else:
        c1, c2 = z[cluster_index - len(tokens), 0:2].astype(int)
        return cluster_index_to_tokens(
            c1, z=z, tokens=tokens
        ) + cluster_index_to_tokens(c2, z=z, tokens=tokens)


if __name__ == "__main__":
    main()
