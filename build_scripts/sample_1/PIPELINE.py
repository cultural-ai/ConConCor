"""
Pipeline for sampling 200 europeana articles + metadata + ocr (where available)
Articles are sampled by content and date query combinations (i.e., 200 per combination)

Run:
    python3 PIPELINE.py
"""

import os


def main():

    # ------
    # As per https://pro.europeana.eu/resources/apis/intro#access, an api key is required to query the eurpeaana database. Please add below:
    # ------
    user_key = "awatement"
    # user_key = "paste your key here"

    # ------
    # catalogue europeana newspaper articles
    # ------
    print(
        'cataloguing the europeana newspaper articles, see "python3 catalogue.py -h" for details.'
    )
    os.system(
        f"python3 catalogue.py password={user_key}"
    )  # output: europeana_catalogue.csv

    # ------
    # populate queries/Contentious.txt, queries/Alternative.txt,
    # queries/Additional.txt with query words and queries/dates_artikel.txt
    # with query dates
    # ------

    # ------
    # catalogue urls to kb articles matching queries, populate europeana id's
    # for corresponding articles, and get metadata for a sample of 200 articles
    # per query combination.
    # ------
    print(
        'catalogue urls to ocrs matching queries and sample metadata for 200 random urls per query in the europeana subset. See "python3 query_kb.py -h for details". '
    )

    metadata_samples_per_query = 200
    if os.path.exists("contentious_words/metadata.json"):
        pass
    else:
        os.system(
            f"python3 query_kb.py -c queries/Contentious.txt queries/dates_artikel.txt -m {metadata_samples_per_query} -save_dir contentious_words"
        )  # output: contentious_words/metadata.json

    if os.path.exists("alternative_words/metadata.json"):
        pass
    else:
        os.system(
            f"python3 query_kb.py -c queries/Alternative.txt queries/dates_artikel.txt -m {metadata_samples_per_query} -save_dir alternative_words"
        )  # output: alternative_words/metadata.json

    if os.path.exists("additional_words/metadata.json"):
        pass
    else:
        os.system(
            f"python3 query_kb.py -c queries/Additional.txt queries/dates_artikel.txt -m {metadata_samples_per_query} -save_dir additional_words"
        )  # output: additional_words/metadata.json

    # ------
    # retrieve ocr articles of the 200 randomly selected articles for which
    # metadata was retrieved.
    # ------
    print(
        "retrieve ocr + metadata for the europeana subset for which metadata was sampled"
    )
    if os.path.exists("contentious_words/get_ocr.json"):
        pass
    else:
        os.system(
            "python3 get_ocr.py -f contentious_words/metadata.json -all -o contentious_words"
        )

    if os.path.exists("alternative_words/get_ocr.json"):
        pass
    else:
        os.system(
            "python3 get_ocr.py -f alternative_words/metadata.json -all -o alternative_words"
        )

    if os.path.exists("additional_words/get_ocr.json"):
        pass
    else:
        os.system(
            "python3 get_ocr.py -f additional_words/metadata.json -all -o additional_words/"
        )


if __name__ == "__main__":
    main()
