import json
import os
import pickle as pkl
import typing

from scipy.cluster.hierarchy import linkage

# useful gensim resources:
# https://github.com/RaRe-Technologies/gensim/wiki/Migrating-from-Gensim-3.x-to-4


def main():

    # script output file paths
    sav_linkage = "clustering/linkage_matrix.pkl"

    # ensure output file dirs exist
    os.makedirs(os.path.dirname(sav_linkage), exist_ok=True)

    # pass of output exists
    if os.path.exists(sav_linkage):
        pass
    else:

        print("creating heirarchical clustering linkage matrix")

        # load the reduced embeddings
        with open("embeddings_reduced/embeddings.pkl", "rb") as f:
            X_2d = pkl.load(f)

        # save labels
        with open("embeddings_reduced/tokens.json", "r") as f:
            json.load(f)

        linkage_matrix = linkage(
            X_2d,
            # model.wv.get_normed_vectors(),
            # model.wv[['boot', 'zee']],
            method="complete",
            metric="euclidean",
        )

        with open(sav_linkage, "wb") as f:
            pkl.dump(linkage_matrix, f)


if __name__ == "__main__":
    main()
