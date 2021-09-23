import csv
import os
import re
import shelve
import typing

import flask_shelve
import pandas as pd
from io import StringIO
from flask import Flask, jsonify, render_template, request, send_file, session, stream_with_context
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response

app = Flask(__name__)
app.config["SHELVE_FILENAME"] = "shelve.db"
flask_shelve.init_app(app)


@app.route("/")
def input():
    return render_template("in.html")


@app.route("/out.html", methods=["GET", "POST"])
def handle_input():

    if request.method == "POST":

        # open persistent database - auto released, no manual intervention
        # required.
        db = flask_shelve.get_shelve("c")

        # handle first opening of db: ensure there's a store of user ids
        # get the input from "/"
        id = request.form["id"]  # prolific id

        # handling existing user
        if id in db:
            url_index = db[id]

        # handling a new user
        else:

            # increment user_counter for the new user
            try:
                db["user_counter"] += 1
            except:  # first user
                db["user_counter"] = 0
            url_index = db["user_counter"]

            # log user, and associated url_index
            db[id] = url_index

        # get user url
        for index, url in enumerate(gen_file_lines("form_urls.txt")):
            if index == url_index:
                break

        return render_template("out.html", url=url)
    else:
        return render_template("in.html")


@app.route("/log")
def download_log():
    def generate():
        data = StringIO()
        w = csv.writer(data)

        # write header
        w.writerow(("user", "counter",  "form name", "url"))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        #for generating form number
        suffices = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

        # write each log item
        form_urls = list(gen_file_lines("form_urls.txt"))
        with shelve.open("shelve.db", "r") as db:
            print(db.items())
            for user_id, url_counter in db.items():  # iterate over user_id: url_index
                if user_id != "user_counter":

                    form_name = lambda i: str((i // 7)+1) + suffices[i % 7]

                    w.writerow((user_id, url_counter, form_name(url_counter), form_urls[url_counter]))
                    yield data.getvalue()
                    data.seek(0)
                    data.truncate(0)

    # add a filename
    headers = Headers()
    headers.set("Content-Disposition", "attachment", filename="log.csv")

    # stream the response as the data is generated
    return Response(
        stream_with_context(generate()), mimetype="text/csv", headers=headers
    )


def gen_file_lines(path: str):
    """Return a generator yielding successive file lines.

    Strips lines of '\n'.

    Args:
        path (str): path to txt file
    """
    with open(path, "r") as f:
        for line in f:
            yield line.strip("\n")


def gen_dir(dir: str = os.getcwd(), *, pattern: str = ".+"):
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


def gen_csv_rows(path: str, *, ignore_rows: typing.List = []):
    """Return a generator yielding successive csv rows.

    Will ignore row indices specified in ignore_rows arg.

    Args:
        path (str): path to csv
        ignore_rows (list): E.g., title row = [0]
    """
    with open(path, "r") as f:
        for index, line in enumerate(csv.reader(f)):
            if index not in ignore_rows:
                yield line


if __name__ == "__main__":
    app.run(port=5000, debug=True)  # debug updates app based on code changes
