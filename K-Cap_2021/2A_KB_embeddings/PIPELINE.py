"""
python3 PIPELINE.py

Fri Aug 27 2021: corrections to text analysis, carry on from same ocrs
"""

import subprocess
import typing


def main():

    # ======
    # NOTE: scripts are skipped where output already exists. 
    # Hence, delete corresponding output where you wish to a script to be
    # re-run in running the pipeline
    # ======

    # ======
    # Build embeddings
    # ======

    # ------
    # for each decade 1890 to 1942, split the avaiable article pool into
    # articles of 1000, and randomly sample 100 articles from 1000 randomly samples splits
    # i.e., randomly sample 100,000 artcles per decade, returning urls.
    # ------
    subprocess.run(["python3", "get_urls.py"])  # output: urls/

    # ------
    # Iterate over urls to ocrs from urls/ and retrieve ocrs.
    #   each ocr record is stored on a newline and subtended by <ocr url=></ocr> tags
    #   paragraphs within a single ocr are separated by <par> uni-tags 
    # ------
    subprocess.run(["python3", "get_ocrs.py"])  # output ocrs/

    # ------
    # Iterate over retrieved ocrs in ocrs/ and return text-analysed versions.
    #   sentences within a paragraph are returned separated by <sent> uni-tags
    # ------
    subprocess.run(["python3", "text_analysis.py"])  # output: text_analysis/

    # ------
    # compile all sents in text_analysis/ in a newline separated file embeddings/sents.txt (stripped of tags);
    # create embeddings for the sents (refer to script embedding parameters)
    # ------
    subprocess.run(["python3", "build_embeddings.py"])  # output: embeddings/

    # ======
    # build a heirarchical clustering matrix
    # ======

    # ------
    # the number of tokens in the resultant embeddings training on 6x100k docs
    # is too large for the KNAW rekenserver to handle in performing
    # heirarchical clustering. Find the token subset which occurs >= 20 times
    # ------
    subprocess.run(["python3", "get_subset.py"])  # output: embeddings/keep_tokens.json

    # ------
    # Get an embeddings subset consisting only of those embeddings in
    # embeddings/keep_tokens.json tokens
    # ------
    subprocess.run(["python3", "get_embeddings_subset.py"])  # output: embeddings_subset/

    # ------
    # Get a set of dim-reduced embeddings via UMAP
    # ------
    subprocess.run(["python3", "get_reduced.py"])  # output: embeddings_reduced/

    # ------
    # Get the heirarchical clustering matrix, based on dim-reduced embeddings
    # clustered based on euclidean distance.
    # ------
    subprocess.run(["python3", "clustering.py"])  # output: clustering/

if __name__ == "__main__":
    main()
