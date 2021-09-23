import itertools
import json
import os
import re
import typing
from time import time

from gensim.models import KeyedVectors, Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
from gensim.models.word2vec import LineSentence


def main():

    #
    # process text-analysed files, extracting sents into sents.txt
    #
    file_names = gen_dir(
        "text_analysis", pattern=".*\.txt$"
    )  # generator of file names of text-analysed files (str)

    file_paths = (
        f"text_analysis/{file_name}" for file_name in file_names
    )  # iterator of file paths (str)

    ocrs = itertools.chain.from_iterable(
        gen_file_lines(file_path) for file_path in file_paths
    )  # iterator of analysed ocr strings with tags in-place (str)

    sents: typing.Iterator[list] = itertools.chain.from_iterable(
        map(get_sents, ocrs)
    )  # iterator of all ocrs as lists of sents

    sav_sents = "embeddings/sents.txt"
    os.makedirs(os.path.dirname(sav_sents), exist_ok=True)

    # pass of sav_sents exists
    if os.path.exists(sav_sents):
        pass
    else:
        print("assembing ocr sents")
        with open(sav_sents, "w") as f:
            f.writelines(
                [sent + "\n" for sent in sents if sent is not None]
            )  # removes empty sentences when saving (None)

    #
    # build embeddings
    #

    # see https://radimrehurek.com/gensim/models/word2vec.html

    # sentences as restartable streamed iteratble
    sav_model = "embeddings/w2v.model"

    # pass if sav_model exists
    if os.path.exists(sav_model):
        pass
    else:
        print("training model")
        start = time()

        # initialise/ train the model
        with open(sav_sents, "r") as f:
            sentences = LineSentence(f)
            model = Word2Vec(
                sentences=sentences,
                vector_size=100,
                window=5,
                min_count=5,
                workers=50,
                sg=1,
                epochs=10,
                compute_loss=True,
                callbacks=[EpochSaver('embeddings/losses.json')]
            )
            model.save(sav_model)
        end = time()
        print(f"total training time = {end-start}")

    #
    # are the embeddings sensible? - find most similar as compared to ...
    #

    print("check:")
    model = Word2Vec.load(sav_model)
    for token in ["schip", "hond", "vrouw"]:
        print(f"\t{token} is most similar to {model.wv.most_similar(positive=[token])}")


class EpochSaver(CallbackAny2Vec):
    """Callback to save model losses by epoch to file."""

    def __init__(self, output_file_path: str):
        self.output_file_path: str = output_file_path
        self.epoch: int = 0
        self.losses: dict = {}

    def on_epoch_end(self, model):

        self.epoch += 1
        self.losses[self.epoch] = model.get_latest_training_loss()

        with open(self.output_file_path, 'w') as f:
            json.dump(self.losses, f)


def get_sents(ocr) -> list:
    """Return a list of sentences taken from text-analysed ocr record.

    Returns [None] if the text-analysed ocr is empty.
    """

    # remove the opening and closing tags
    splits: list = [
        split for split in re.split(r"(<ocr .*?>|</ocr>)", ocr) if split != ""
    ]

    if len(splits) == 3:  # the usual case ... if the text-analysed ocr isn't empty
        open_tag, text, close_tag = splits
        paragraphs: list = text.split("<par>")  # list of paragraphs (str)
        sents: list = list(
            itertools.chain.from_iterable(
                (paragraph.split("<sent>") for paragraph in paragraphs)
            )
        )  # list of sentences (str)
    else:
        open_tag, close_tag = splits
        sents = [None]

    return sents


def gen_file_lines(path: str, *, strip: list = ["\n"]) -> typing.Generator:
    """Return a generator yielding successive file lines.

    Args:
        path (str): path to txt file
        strip (list): a list of callables to be recursively applied to each line

    Example:
        gen_file_lines(path, strip = [])
    """
    with open(path, "r") as f:
        for line in f:

            if strip:
                # recursively apply strip(), for each entry in strip arg
                state = line
                for entry in strip:
                    state = state.strip(entry)
                # yield stripped line
                yield state
            else:
                yield line


def gen_dir(dir: str = os.getcwd(), *, pattern: str = ".+") -> typing.Generator:
    """Return a generator yielding filenames in a directory, optionally matching a pattern.

    Args:
        dir (str): [default: script dir]
        pattern (str): filename pattern to match against [default: any file]
    """

    for filename in os.listdir(dir):
        if re.search(pattern, filename):
            yield filename
        else:
            continue


if __name__ == "__main__":
    main()
