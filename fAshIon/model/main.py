import json
import pprint
import math

import numpy as np
import pandas as pd

from nltk import word_tokenize
from fAshIon.model.word_representation import add_ontology, preprocess_data
from fAshIon.model.clustering import skipgram_clustering, get_cluster_dict, build_sims_matrix
from fAshIon.Utils import get_data_for_neural_network, dump_output_file, read_output_file, get_same_set_ontology, phrase_model_id

pd.set_option("display.max_rows", 50000)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 2500)

data_index = 0


# ++++++ Data access ++++++
# noinspection PyShadowingNames,SpellCheckingInspection
def get_data(name="train_no_dup.json", cached=False):
    df, summary = None, None
    if cached:
        df = read_output_file('raw_df')
        summary = read_output_file('raw_sum')
    else:
        raw_data = get_data_for_neural_network(data_version=name)
        # read json file
        with open(raw_data) as f:
            data_file = json.load(f)
        # remove unnecessary information
        data_list = []
        for fashion_set in data_file:
            for key in {"date", "desc", "image", "set_url"}:
                fashion_set.pop(key, None)
            set_info = np.array([fashion_set["set_id"], fashion_set["likes"], fashion_set["views"]])
            for item in fashion_set["items"]:
                item.pop("image", None)
                item_info = np.array([item["categoryid"], item["name"]])
                fashion_item = np.concatenate([set_info, item_info])
                data_list.append(fashion_item)

        df_headers = np.array(["s_id", "s_likes", "s_views", "i_category_id", "i_name"])

        # load item records to panda dataframe
        df = pd.DataFrame(columns=df_headers, data=data_list, dtype=np.int64)
        df["s_likes"] = pd.to_numeric(df["s_likes"])
        df["s_views"] = pd.to_numeric(df["s_views"])
        df["i_name"] = df["i_name"].apply(lambda x: set(preprocess_data(word_tokenize(x))))

        # statistics
        outfit_number = df["s_id"].unique().shape[0]
        max_s_likes = df["s_likes"].max()
        min_s_likes = df["s_likes"].min()
        max_s_views = df["s_views"].max()
        min_s_views = df["s_views"].min()
        avg_s_likes = round(df["s_likes"].mean(), 3)
        avg_s_views = round(df["s_views"].mean(), 3)
        item_number = df.shape[0]

        summary = {
            "o_total": outfit_number,
            "o_max_like": max_s_likes,
            "o_min_like": min_s_likes,
            "o_avg_like": avg_s_likes,
            "o_max_view": max_s_views,
            "o_min_view": min_s_views,
            "o_avg_view": avg_s_views,
            "i_total": item_number,
        }

        def find_dup_score(user_rating, user_avg, modifier, normalizer=0.9):
            score = user_rating / float(user_avg)
            score = math.floor(score * modifier)
            if score > 10:
                score = 10 + math.floor((score - 10) ** normalizer)
            return score

        df['dup_score'] = df['s_likes'].apply(lambda x: find_dup_score(x, summary["o_avg_like"], 2)) \
            + df['s_views'].apply(lambda x: find_dup_score(x, summary["o_avg_view"], 2, 0.7))
        dump_output_file(df, 'raw_df')
        dump_output_file(summary, "raw_sum")

    return df, summary


if __name__ == "__main__":
    # ####################################################################
    # Clustering model related
    retrain_model = True
    new_raw_data = False
    new_onto_def = False
    retrain__matrix = True
    # if len(sys.argv) > 1:
    #     if str(sys.argv[1]).lower() in ["y", "yes", "retrain"]:
    #         retrain_model = True
    #     if str(sys.argv[2]).lower() in ["y", "yes", "retrain"]:
    #         new_raw_data = True
    onto_df = read_output_file("onto_df")
    print(onto_df.head(7))
    if retrain_model:
        print("Retraining")
        if new_raw_data:
            new_onto_def = True
        if new_onto_def:
            df, summary = get_data(cached=not new_raw_data)
            onto_df = add_ontology(df)
            onto_df = get_same_set_ontology(onto_df)
            dump_output_file(onto_df, "onto_df")

        onto_df = read_output_file("onto_df")
        models = [
            # ["item"],
            # ["color"],
            # ["item", "material"],
            # ["item", "color"],
            ["material", "color"],
            # ["item", "color", "material"]
        ]
        pass
        for model in models:
            print("**********************************")
            print("start training")
            pprint.pprint(model)
            print("**********************************")
            cluster = skipgram_clustering(onto_df, model, phrase_model_id(model))
            dump_output_file(cluster, phrase_model_id(model, "_cluster"), "fAshIon/output/cluster")
            print("**********************************")
            print("THe cluster is retrained:")
            pprint.pprint(model)
            print("**********************************")
        print("The following clusters are retrained:")
        pprint.pprint(models)

    if retrain__matrix:
        onto_attrs = [
            ["item"],
            ["color"],
            ["item", "material"],
            ["item", "color"],
            ["material", "color"],
            # ["item", "color", "material"]
        ]
        for onto_attr in onto_attrs:
            cluster = read_output_file(phrase_model_id(onto_attr, "_cluster"), "fAshIon/output/cluster")
            w2i, i2w = get_cluster_dict(cluster, onto_attr)
            sims_matrix = build_sims_matrix(cluster, onto_attr)
            # pprint.pprint(sims_matrix["matrix"])
            dump_output_file(sims_matrix, phrase_model_id(onto_attr, "_matrix"), "fAshIon/output/matrix")
            print("===========================" +
                  phrase_model_id(onto_attr, "_matrix") +
                  " done===========================")

        # sims_matrix = read_output_file(phrase_model_id(["item"], "_matrix"))
        # print(sims_matrix["axis1"])
        # print(sims_matrix["axis2"])
        #
    # df, summary = get_data(cached=True)
    # pprint.pprint(df.head(30))
    print("Finish main")
