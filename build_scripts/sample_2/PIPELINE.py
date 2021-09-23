"""

sample contentious, alternative and additional extracts

Run:
    python3 PIPELINE.py
"""
import os


def main():

    os.system(
        "python3 sample.py -data ../score/contentious_words/scored.json -q sampling_criteria/contentious_criteria.txt -s sampling_criteria/spatial.txt -a 2 -n 2 -N 1200 -sav_dir contentious_words"
    )

    os.system(
            "python3 sample.py -data ../score/alternative_words/scored.json -q sampling_criteria/alternative_criteria.txt -s sampling_criteria/spatial.txt -a 2 -n 12 -N 1200 -sav_dir alternative_words"
        )

    os.system(
        "python3 sample.py -data ../score/additional_words/scored.json -q sampling_criteria/additional_criteria.txt -s sampling_criteria/spatial.txt -a 2 -n 1 -N 300 -sav_dir additional_words"
    )

if __name__ == "__main__":
    main()
