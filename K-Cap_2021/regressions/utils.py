import numpy as np
import pandas as pd

from tqdm import tqdm


def annotation_to_var(ann):
    if ann == "Niet omstreden": return 0
    if ann == "Omstreden naar huidige maatstaven": return 1
    if ann == "Weet ik niet": return 2
    return 3


def annotator_ids_to_var(ids):
    num_ids = dict(zip(sorted(ids), range(len(ids))))    
    return ids.apply(lambda i: num_ids[i])


def remove_target_from_context(row):
    return row.text.replace(row.target_compound_bolded, " ") #"[MASK]")


def get_DF():
    extr = pd.read_csv("CCC_embeddings/ccc_dataset/Extracts.csv").set_index("extract_id")
    ann = pd.read_csv("CCC_embeddings/ccc_dataset/Annotations.csv")
    
    data = pd.concat([
            ann[["response", "anonymised_participant_id"]], 
            extr.loc[ann.extract_id][["target", "text", "target_compound_bolded"]].reset_index()
                 ], axis=1).set_index("extract_id")

    data["y"] = data.response.apply(annotation_to_var)
    data = data[data.y < 2]
    
    data["annotator_x"] = annotator_ids_to_var(data.anonymised_participant_id)
    data["context_wo_target"] = data.apply(remove_target_from_context, axis=1)
    return data
    
    
    
def get_indices(words, word_ls):
    inds = {}
    for w in tqdm(sorted(words)):
        try:
            inds[w] = word_ls.index(w)
        except ValueError:
            pass

    return inds
