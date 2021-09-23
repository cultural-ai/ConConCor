import json
import os
import pickle as pkl
import typing
from copy import copy
from time import time

import numpy as np
import umap
from gensim.models import KeyedVectors, Word2Vec
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial import distance
from sklearn.manifold import TSNE

# useful gensim resources:
# https://github.com/RaRe-Technologies/gensim/wiki/Migrating-from-Gensim-3.x-to-4


def main():

    #
    # load dim-reduced embeddings (if exist from previous clustering.py run)
    #

    # script output files
    sav_reduced_embeddings = "embeddings_reduced/embeddings.pkl"
    sav_tokens = "embeddings_reduced/tokens.json"

    # ensure output dir exists
    os.makedirs(os.path.dirname(sav_reduced_embeddings), exist_ok=True)

    # pass if output exists
    if os.path.exists(sav_reduced_embeddings) and os.path.exists(sav_tokens):
        pass
    else:

        print('loading embeddings and performing dim-reduction')

        with open('embeddings_subset/embeddings.pkl', 'rb') as f:
            X = pkl.load(f)

        with open('embeddings_subset/tokens.json', 'r') as f:
            tokens = json.load(f)

        X_2d = umap.UMAP(n_components=2).fit_transform(X)

        # save the dim reduced embeddings & tokens
        with open(sav_reduced_embeddings, "wb") as f:
            pkl.dump(X_2d, f)

        with open(sav_tokens, "w") as f:
            json.dump(tokens, f)


if __name__ == "__main__":
    main()
