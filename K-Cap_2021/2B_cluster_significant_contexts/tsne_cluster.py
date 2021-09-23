"""
Plot the \n-separated tokens in context_tokens.txt, and non-context_tokens.txt on a 2-d embeddings space.

Process
* load the full embeddings set and separate tokens from vectors;
* load tokens to be plotted (in embedding space)
* Get t-SNE reduced vectors wrt for the tokens and plot
"""
import json
import os
import pickle as pkl
import typing
from copy import copy
from time import time

import numpy as np
from gensim.models import KeyedVectors, Word2Vec
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial import distance
from sklearn.manifold import TSNE

# useful gensim resources:
# https://github.com/RaRe-Technologies/gensim/wiki/Migrating-from-Gensim-3.x-to-4

def main():

    # script load files
    load_embeddings = "../2A_KB_embeddings/embeddings/w2v.model"
    load_contentious_context_tokens = "context_tokens.txt"
    load_non_contentious_context_tokens = "non-context_tokens.txt"

    # ------
    # load embeddings
    # ------ 
    print("Loading embeddings")

    model = Word2Vec.load(load_embeddings)

    # extract ndarray of embeddings
    X: np.ndarray = model.wv.get_normed_vectors()  # [vocab length x hidden dim]
    embeddings_tokens: list = list(
        model.wv.key_to_index
    )  # i.e., tokens[0] is the token corresponding to X[0]

    # create hash
    token_to_index = {token: index for index, token in enumerate(embeddings_tokens)}

    print("loading the significant context tokens")

    # ------
    # load significant context tokens
    # ------
    with open(load_contentious_context_tokens, "r") as f:
        contentious_tokens = [line.strip("\n") for line in f.readlines()]

    with open(load_non_contentious_context_tokens, "r") as f:
        non_contentious_tokens = [line.strip("\n") for line in f.readlines()]

    context_tokens = contentious_tokens + non_contentious_tokens

    # ------
    # Get the embedding subset for context tokens
    # ------
    contexts_present = []
    contexts_missing = []
    for ct in context_tokens: 
        if ct in embeddings_tokens:
            contexts_present.append(ct)
        else:
            contexts_missing.append(ct)

    X = X[[token_to_index[ct] for ct in contexts_present], :]  # matrix has same order as contexts_present list

    # ------
    # Perform TSNE reduction
    # ------
    print("Perform tsne dim reduction")

    X_2d = TSNE(n_components=2).fit_transform(X)

    # # save the dim reduced embeddings & tokens
    # with open(sav_reduced_embeddings, "wb") as f:
    #     pkl.dump(X_2d, f)

    # with open(sav_tokens, "w") as f:
    #     json.dump(tokens, f)

    # ------
    # Plot
    # ------

    #create a new figure and set the x and y limits
    fig, axes = plt.subplots(figsize=(5,5))
    axes.set_xlim(-15,15)
    axes.set_ylim(-15,15)

    #loop through (2d embeddings, context token) data points and plot each point 
    for index, e in enumerate(X_2d):
        ct = contexts_present[index]

        #add the data point as text
        if ct in contentious_tokens:
            plt.scatter(x = e[0], y=e[1], c='red')
        else:
            plt.scatter(x = e[0], y=e[1], c='green')

        plt.annotate(ct, 
                     (e[0], e[1]),
                     horizontalalignment='right',
                     verticalalignment='top',
                     size=10,
                     ) 

    plt.show()



if __name__ == "__main__":
    main()
