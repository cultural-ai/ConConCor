import json
import os
import pickle as pkl
import typing

import numpy as np
from gensim.models import Word2Vec

# useful gensim resources:
# https://github.com/RaRe-Technologies/gensim/wiki/Migrating-from-Gensim-3.x-to-4


def main():

    # file paths to script outputs
    sav_reduced_embeddings = "embeddings_subset/embeddings.pkl"
    sav_tokens = "embeddings_subset/tokens.json"
    os.makedirs(os.path.dirname(sav_reduced_embeddings), exist_ok=True)

    # pass if output already exists
    if os.path.exists(sav_reduced_embeddings) and os.path.exists(sav_tokens):
        pass
    else:

        # load the gensim embeddings
        print("loading the embeddings")
        model_filename = "embeddings/w2v.model"
        model = Word2Vec.load(model_filename)

        # extract ndarray of embeddings
        X: np.ndarray = model.wv.get_normed_vectors()  # [vocab length x hidden dim]
        tokens: list = list(
            model.wv.key_to_index
        )  # i.e., tokens[0] is the token corresponding to X[0]

        print(f"\timported embeddings vocab length={len(tokens)}")

        # consider only a subset of the embeddings if keep_token.json exists
        sav_keep_tokens: str = "embeddings/keep_tokens.json"
        if os.path.exists(sav_keep_tokens):
            print(f"\tbuilding an embedding subset as per {sav_keep_tokens}")

            # load keep_tokens
            with open(sav_keep_tokens, "r") as f:
                keep_tokens: set = set(json.load(f))

            # from keep_tokens, create list/set of indices to remove wrt., X and tokesng
            remove_indices: list = []
            for index, token in enumerate(tokens):
                if token not in keep_tokens:
                    remove_indices.append(index)
            remove_set = set(remove_indices)  # remove_indices as a set

            # get X, tokens minus remove_indices
            X = np.delete(X, remove_indices, axis=0)
            tokens = [t for index, t in enumerate(tokens) if index not in remove_set]

            print(f"\tembeddings subset vocab length={X.shape[0]}")
        else:

            print(f"\t{sav_keep_tokens} does not exist, keeping full embedding set")

        # save X and tokens
        os.makedirs(os.path.dirname(sav_reduced_embeddings), exist_ok=True)
        with open(sav_reduced_embeddings, "wb") as f:
            pkl.dump(X, f)

        with open(sav_tokens, "w") as f:
            json.dump(tokens, f)


if __name__ == "__main__":
    main()
