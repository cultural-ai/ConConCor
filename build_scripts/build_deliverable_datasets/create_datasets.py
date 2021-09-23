"""
Requires in folder:
    * unanonymised_annotations.csv from get_form_data/
    * DataSheet2.csv from assemble_forms/
    * prolific_export.csv, i.e., export from prolific.

Addtional user-defined inputs
    * see lines 126-135, uses the metadata.json files built in get_extracts for
    Contentious, Alternative & Additonal target word streams, used to assemble
    the extracts.

Outputs:
    * participant_id_index.csv: a table of participant_id:anonymised_participant_id:
    * Extracts.csv: a catalogue of extracts, referencing extract_id and article_url
        * unchanged from DataSheet2
    * Annotations.csv: anonymised participant responses, references both extract_id and anonymised_participant_id
    * Demographics.csv: prolific export data with anonymised_participant_id:
        * contains only those participants in Annotations.csv
    * Metadata.csv: metadata associated with article_url:
        * for those article_urls in Extracts.csv only
"""

import csv
import json

import numpy as np
import pandas as pd


def main():

    datasheet1: pd.DataFrame = pd.read_csv("unanonymised_annotations.csv")
    datasheet2: pd.DataFrame = pd.read_csv("DataSheet2.csv")
    prolific: pd.DataFrame = pd.read_csv("prolific_export.csv")

    # ------
    # Create participant_index.csv (and conversion dict, pid)
    # ------

    # get participant_ids and anonymised_participant ids as series
    participants: np.ndarray = datasheet1["participant_id"].unique()

    anonymised_participants: pd.Series = pd.Series(
        [i for i in range(len(participants))]
    )

    # create hash for conversion
    pid = dict(
        zip(
            participants,
            anonymised_participants,
        )
    )

    # save hash as csv
    pd.DataFrame(
        {
            "participant_id": participants,
            "anonymised_participant_id": anonymised_participants.values,
        }
    ).to_csv("participant_index.csv", index=False)

    # ------
    # create Demographics.csv
    # ------

    print("Creating Demographics.csv")
    # take the prolific data subset for only those participants present in Datasheet1.csv
    demographics: pd.DataFrame = (
        prolific.loc[
            prolific["participant_id"].isin(participants),
            [
                "participant_id",
                "time_taken",
                "age",
                "Country of Birth",
                "Current Country of Residence",
                "Employment Status",
                "First Language",
                "Fluent languages",
                "Nationality",
                "Sex",
                "Student Status",
            ],
        ]
        .copy()
        .reset_index(drop=True)
    )

    # add anoymised id column and shift to front
    demographics["anonymised_participant_id"] = demographics["participant_id"].apply(
        lambda i: pid[i]
    )
    col = demographics.pop("anonymised_participant_id")
    demographics.insert(0, col.name, col)

    # save Demographics.csv (free of original non-anonymouse participant_id col)
    demographics.drop(columns=["participant_id"]).to_csv(
        "Demographics.csv", index=False
    )

    # ------
    # Save datasheet2.csv as Extracts.csv
    # ------
    print("Creating Extracts.csv")
    datasheet2: pd.DataFrame = pd.read_csv("DataSheet2.csv")
    datasheet2.to_csv("Extracts.csv", index=False)

    # ------
    # Create Annotations.csv
    # ------
    print("Creating Annotations.csv")
    annotations = datasheet1.copy()

    # add anonymised_participant_id and move to front
    annotations["anonymised_participant_id"] = annotations.loc[
        :, "participant_id"
    ].apply(lambda i: pid[i])
    col = annotations.pop("anonymised_participant_id")
    annotations.insert(0, col.name, col)

    # save to csv (from of original pariticpant_id col)
    annotations.drop(columns=["participant_id"]).to_csv("Annotations.csv", index=False)

    # ------
    # Create Metadata.csv
    # ------
    print("loading metadata.json")
    with open("../../../get_extracts/p_samples/metadata.json") as f:
        metadata_p = json.load(f)
        metadata_p.pop("queries")
    with open("../../../get_extracts/n_samples/neg_samples_metadata.json") as f:
        metadata_n = json.load(f)
        metadata_n.pop("queries")
    with open("../../../get_extracts/additional_samples/additional_metadata.json") as f:
        metadata_a = json.load(f)
        metadata_a.pop("queries")

    # join the metadata
    metadata_master = {
        key: m for key, m in metadata_p.items() if m["kb_oai_metadata_queried"]
    }
    metadata_master.update(
        {key: m for key, m in metadata_n.items() if m["kb_oai_metadata_queried"]}
    )
    metadata_master.update(
        {key: m for key, m in metadata_a.items() if m["kb_oai_metadata_queried"]}
    )

    print("getting metadata for extract urls")
    metadata = [
        [
            "url",
            "europeana_issue_id",
            "datestamp",
            "date",
            "publisher",
            "spatial_distribution",
            "spatial_origin",
            "languages",
        ]
    ]

    for url in datasheet2["url"]:
        try:
            m = metadata_master[url]
            metadata.append(
                [
                    url,
                    m["europeana_issue_id"],
                    m["kb_oai_metadata"]["datestamp"],
                    m["kb_oai_metadata"]["date"],
                    m["kb_oai_metadata"]["publisher"],
                    m["kb_oai_metadata"]["spatial_distribution"],
                    m["kb_oai_metadata"]["spatial_origin"],
                    ", ".join(m["kb_oai_metadata"]["language"]),
                ]
            )
        except:
            metadata.append([url, 0, 0, 0, 0, 0, 0])

    with open("Metadata.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(metadata)


if __name__ == "__main__":
    main()
