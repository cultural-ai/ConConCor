import json
import pickle as pkl
import typing
from collections import defaultdict
from pprint import pp

import numpy as np
from scipy.cluster.hierarchy import fcluster


def main():

    #
    # need to make sense of clusters
    #

    # load the linkag
    sav_linkages = "clustering/linkage_matrix.pkl"
    with open(sav_linkages, "rb") as f:
        Z: np.ndarray = pkl.load(f)

    sav_labels = "clustering/labels.json"
    with open(sav_labels, "rb") as f:
        tokens: list = json.load(f)

    # examine various cluster granularities
    token_cluster_index: np.ndarray = fcluster(Z, 20, criterion="maxclust")

    # build the cluster dict
    clusters = defaultdict(list)
    for token_index, cluster_index in enumerate(token_cluster_index):
        token = tokens[token_index]
        clusters[cluster_index].append(token)

    pp(clusters)


if __name__ == "__main__":
    main()
