"""{Build token: cluster index}, hashes for each specified granularity level in the user-defined list 'clustering_levels_to_consider'

Output: level_xx_hash.json hash to /cluster_hashes
"""

import json
import os
import pickle as pkl
import typing

import numpy as np


def main():

    #
    # user-defined vars
    #
    clustering_levels_to_consider = [12]

    # consider different cluster granulaties, i.e., snip level from leaf
    for clustering_level in clustering_levels_to_consider:

        # load the linkage matrix
        sav_linkages = "heirarchical_clustering/linkage_matrix.pkl"
        with open(sav_linkages, "rb") as f:
            z: np.ndarray = pkl.load(f)

        # load the list of tokens (which corresponds to the linkage matrix)
        # i.e., i in tokens[i], corresponds to cluster i referenced in z[:,0:2]
        sav_tokens = "heirarchical_clustering/tokens.json"
        with open(sav_tokens, "rb") as f:
            tokens: list = json.load(f)

        # see link, below, on interpreting z, i.e., cluster_index1, cluster_index2, dist, cluster size
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.fcluster.html

        clusters: typing.Generator = gen_clusters(
            level=clustering_level, z=z, tokens=tokens
        )  # generator of (cluster_index, list of tokens) of each cluster for the current cut 'level'

        # build a hash, to translate token to cluster index for given granularity
        h: dict = {
            token: cluster_index
            for cluster_index, cluster in clusters
            for token in cluster
        }

        # save
        sav = f"cluster_hashes/level_{clustering_level}_hash.json"
        os.makedirs(os.path.dirname(sav), exist_ok=True)
        with open(sav, "w") as f:
            json.dump(h, f, indent=4)


def gen_clusters(level: int = 1, *, z: np.ndarray, tokens: list) -> typing.Generator:
    """Return a generator of (cluster_index, list of tokens) of each cluster
    for the current cut 'level'.
    """

    # add an 'operation index' column to z
    x: np.ndarray = np.hstack(
        (z, np.array([i for i in range(z.shape[0])]).reshape(-1, 1))
    )
    # note: cluster_index = x[:,4] + len(tokens) is the index of the cluster created by the operation
    # cluster indices 0 to len(tokens) - 1, corresponds to the individual tokens

    #
    # iterate over each cut level (from leafs) until at specified 'level'
    # and collect z_rows_of_interest, an iterable of z row indices, representing the clusters wrt., cut 'level'
    #
    seen_z_rows = []  # all z row clusters seen in previous levels
    seen_cluster_indices = [index for index, token in enumerate(tokens)]

    for i in range(1, level + 1):  # i.e., cluster 1 to level

        x_dropped: np.ndarray = np.delete(
            x, seen_z_rows, axis=0
        )  # i.e., drop clusters seen at previous level

        x_i: np.ndarray = x_dropped[
            [row.all() for row in np.isin(x_dropped[:, 0:2], seen_cluster_indices)]
        ]  # the bit of x that lists the clusters in the current cut level, i.e., those clusters that reference only previously seen cluster_indices

        z_rows_of_interest: np.ndarray = x_i[:, 4].astype(int)

        seen_z_rows += [row for row in z_rows_of_interest]
        seen_cluster_indices += [z_row + len(tokens) for z_row in x_i[:,4]]

    # generate a (cluster_index, list of tokens) for each cluster of the current cut 'level'
    for row in z_rows_of_interest:
        cluster_index = int(x[row, 4]) + len(
            tokens
        )  # i.e., the 'true' cluster indices of z[row,4] + len(tokens) - 1
        yield (
            cluster_index,
            cluster_index_to_tokens(cluster_index, z=z, tokens=tokens),
        )


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
