import os
import re
import subprocess


def main():

    # ------
    # Build token: cluster hashes for clusters 1 step to 10 steps form the
    # leafs (tokens)
    # ------
    subprocess.call(["python3", "build_cluster_hashes.py"])  # output cluster_hashes/

    # ------
    # Build stats wrt., associations
    # ------
    subprocess.call(["python3", "get_associations.py"])


if __name__ == "__main__":
    main()
