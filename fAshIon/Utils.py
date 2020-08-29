import json
import pickle
import pprint

import pandas as pd
import numpy as np

from os.path import dirname, join, normpath


def get_data_for_neural_network(data_version="train_no_dup.json"):
    """
    :param data_version: indicating which dataset to be used, in between [train, valid, test]
    :return: the absolute path of the target file
    """
    project_root = dirname(dirname(__file__))
    data_name = "fAshIon/artefacts/training/" + data_version
    ret_path = normpath(join(project_root, data_name))
    return ret_path


def flatten(l):
    """
    :param l: input list of list
    :return: flattened list
    """
    return [item for sublist in l for item in sublist]


def dump_output_file(data, filename, output_path="fAshIon/output", json_format=False):
    """
    save data in a pickle binary file
    :param data: input
    :param filename: saved file name
    :param output_path: file path of saved file
    :return: none
    """
    project_root = dirname(dirname(__file__))
    full_path = normpath(join(project_root, output_path, filename))
    if json_format:
        with open(full_path + ".json", "w",  encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    else:
        with open(full_path, "wb") as file:
            pickle.dump(data, file)


def read_output_file(filename, output_path="fAshIon/output", json_format=False):
    """
    read pickle binary file
    :param json_format:
    :param filename: target file name
    :param output_path: path to target file
    :return: data in target file
    """
    project_root = dirname(dirname(__file__))
    full_path = normpath(join(project_root, output_path, filename))
    if json_format:
        with open(full_path + ".json") as file:
            return json.load(file)
    else:
        with open(full_path, "rb") as file:
            return pickle.load(file)


def get_ontology_def(ontology_file="fAshIon/artefacts/ontology.json"):
    """
    Phrase ontology definition from file,
    :param ontology_file: target file
    :return:
    """
    project_root = dirname(dirname(__file__))
    onto_dict = normpath(join(project_root, ontology_file))
    with open(onto_dict) as f:
        onto_dict = json.load(f)

    onto_def = {"def": onto_dict[0]["def_"],
                "context_multiplier": onto_dict[1]["context_multiplier"],
                "item2item_weight": onto_dict[1]["item2item_weight"],
                "max_ids": {}}
    for i in range(len(onto_dict[0]["def_"])):
        key = onto_dict[0]["def_"][i]
        # onto_dict[i + 1] because onto_dict[0] is always definition of attributes
        onto_def[key] = onto_dict[i + 1][key]
        # reverse lookup from id to word
        if key != "context":
            onto_def[key + "_id_lookup"] = {v[0]: k for i, (k, v) in enumerate(onto_def[key].items())}
        # topics within ontology attribute
        if "def_topic_" in onto_dict[i + 1]:
            key_topic = key + "_topic"
            onto_def[key_topic] = onto_dict[i + 1]["def_topic_"]
        # max ids for each ontology attribute
        if "def_id_range" in onto_dict[i + 1]:
            key_ids_range = onto_dict[i + 1]["def_id_range"]
            onto_def["max_ids"][key] = key_ids_range[len(key_ids_range) - 1].split("-")[1]

    # reverse lookup from id to word for context
    onto_def["context_id_lookup"] = {i: k for i, k in enumerate(onto_def["context"])}

    # pprint.pprint(onto_def, indent=4)
    return onto_def


def get_same_set_ontology(dataframe):
    """
    Group ontology keywords within the same set, each row in returned dataframe represent a set
    :param dataframe: dataframe with ontology columns
    :return: new dataframe consist of grouped ontology keywords
    """
    onto_def = get_ontology_def()
    onto_attr = onto_def["def"][0: len(onto_def["def"]) - 1]
    sets = dataframe.groupby("s_id")  # , as_index=False)

    onto_df = pd.DataFrame()
    onto_df["dup_score"] = sets["dup_score"].apply(lambda x: np.mean(x))
    for attr in onto_attr:
        onto_df[attr] = sets[attr].apply(lambda x: flatten(list(x)))
    return onto_df


# def get_onto_word_idx_dict(onto_attr):
#     """
#     get custom defined id for ontology attributes based on ontology definition
#     :param onto_attr: selected attributes
#     :return: lookup dictionary and reverse lookup dictionary
#     """
#     onto_def = get_ontology_def()
#     if len(onto_attr) == 1:
#         word2idx = {k: v[0] for i, (k, v) in enumerate(onto_def[onto_attr[0]].items())}
#         idx2word = onto_def[onto_attr[0] + "_id_lookup"]
#     else:
#         word2idx = {}
#         idx2word = {}
#         id_shift = 0
#         for attr in onto_attr:
#             word2idx.update({k: int(v[0]) + id_shift for i, (k, v) in enumerate(onto_def[attr].items())})
#             idx2word.update({int(v[0]) + id_shift: k for i, (k, v) in enumerate(onto_def[attr].items())})
#             id_shift += int(onto_def["max_ids"][attr]) + 1
#     return word2idx, idx2word


def get_word_idx_dict(onto_attr):
    """
    get lookup dictionary with compacted id for ontology attributes
    :param onto_attr: selected attributes
    :return: lookup dictionary and reverse lookup dictionary
    """
    onto_def = get_ontology_def()
    if len(onto_attr) == 1:
        word2idx = {k: i for i, (k, v) in enumerate(onto_def[onto_attr[0]].items())}
        idx2word = {i: k for i, (k, v) in enumerate(onto_def[onto_attr[0]].items())}
    else:
        word2idx = {}
        idx2word = {}
        id_shift = 0
        for attr in onto_attr:
            word2idx.update({k: i + id_shift for i, (k, v) in enumerate(onto_def[attr].items())})
            idx2word.update({i + id_shift: k for i, (k, v) in enumerate(onto_def[attr].items())})
            id_shift += int(len(onto_def[attr].items()))
    return word2idx, idx2word


def phrase_model_id(onto_attr, suffix=""):
    model_id = onto_attr[0]
    for i in range(1, len(onto_attr)):
        model_id += "_" + onto_attr[i]
    model_id += suffix
    return model_id


def normalize_list(l):
    return [val / float(total_sum) for total_sum in [sum(l)] for val in l]


get_ontology_def()


def phrase_user_file(user_name, user_id):
    return str(user_id) + "_" + user_name
