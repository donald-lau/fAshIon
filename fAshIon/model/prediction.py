# # TODO: for existing words simply use shortest cosine distance
# # TODO: for new words use learned embedding to train a model, get embedding for new word and repeat above
# import re
# from tempfile import gettempdir
#
# import tensorflow as tf
#
# from fAshIon.Utils import get_ontology_def, read_output_file, flatten
#
#
# # def load_graph(graph_name):
# #     model_path = "./model_log/" + graph_name + "/"
# #     model = model_path + graph_name + ".meta"
# #     sess = tf.Session()
# #     saver = tf.train.import_meta_graph(model)
# #     saver.restore(sess, tf.train.latest_checkpoint(model_path))
# #
# #     graph = tf.get_default_graph()
# #     return graph
# #
# #
# # def predict_with_single_graph(graph, input):
# #     with tf.session(graph=graph) as session:
# #         pass
# #
# #     for op in graph.get_operations():
# #         print(str(op.values))
# #     print("load")
#
#
# def closest_distance_keywords(learned_embeddings, subontology_def, input_item, targets=30):
#     """
#     Return a list of similar keywords based on near cosine distance
#     :param learned_embeddings: a dictionary consist of the keyword labels and corresponding word embedding vector
#     :param subontology_def: ontology definition for the corresponding category, e.g.
#     :param input_item: input string of the keywords
#     :param targets: number of closest keywords to be returned
#     :return: [(similarity, id, label, topic)]
#     """
#     labels = learned_embeddings["labels"]
#     embeddings = learned_embeddings["final_embeds"]
#
#     def find_cos_sim(v1, v2):
#         a = tf.placeholder(tf.float32, shape=[None], name="input_placeholder_a")
#         b = tf.placeholder(tf.float32, shape=[None], name="input_placeholder_b")
#         normalize_a = tf.nn.l2_normalize(a, 0)
#         normalize_b = tf.nn.l2_normalize(b, 0)
#         cos_similarity = tf.reduce_sum(tf.multiply(normalize_a, normalize_b))
#         sess = tf.Session()
#         cos_sim = sess.run(cos_similarity, feed_dict={a: v1, b: v2})
#         return cos_sim
#
#     def find_subtopic(keyword):
#         for k, v in subontology_def.items():
#             if keyword in v:
#                 return k
#
#     # TODO: check if is better to use tf.nn.top_k
#     if input_item in labels:
#         input_position = labels.index(input_item)
#         ret = []
#         for i in range(len(labels)):
#             sim = find_cos_sim(embeddings[input_position], embeddings[i])
#             # return similarity, id, label, topic
#             # TODO: look up topic
#
#             ret.append((sim, i, labels[i], find_subtopic(labels[i])))
#         ret.sort(reverse=True)
#         # start from index 1 since the first one should always be search word itself
#         return ret[0][3], ret[1:targets + 1]
#
#     else:
#         # TODO: implement neural network to get embeddings for unseen word
#         print("Have not implemented closest_distance_keywords for unseen word" + input_item)
#     pass
#
#
# def naive_keywords_search(all_embeddings, input_item):
#     """
#     Find respective similar keywords for each words in the item
#     :param all_embeddings: dictionary of all learned embeddings
#     :param input_item: (multiple) words describing a single fashion item
#     :return: {keyword: (topic, subtopic, [close key words])}
#     """
#     keywords = re.split(r"\s", input_item)
#     keywords = list(filter(None, keywords))
#     onto_def = get_ontology_def()
#     close_words = {}
#     for keyword in keywords:
#         found = False
#         # expensive
#         for k, v in onto_def.items():
#             if keyword in v:
#                 sub_ontology = onto_def[k + "_full"]
#                 keyword_subonto, closest_words = closest_distance_keywords(all_embeddings[k], sub_ontology, keyword)
#                 close_words[keyword] = (k, keyword_subonto, closest_words)
#                 found = True
#                 break
#         if not found:
#             print("Have not implemented naive_keywords_search for unseen word: " + keyword)
#     return close_words
#
#
# def naive_full_prediction(search_phrase):
#     # TODO: only item and color embeddings right now
#     # load ontology vocabs
#     all_embeddings = {"item": read_output_file("class_embeddings"),
#                       "color": read_output_file("color_embeddings")}
#     items = re.split("[,;]", search_phrase)
#
#     # load ontology classes
#     classes = {}
#     onto_def = get_ontology_def()
#     for i in onto_def["class_topic"]:
#         classes[i] = False
#
#     rec_class_ = []
#     closest_keywords = []
#     rec_class = []
#     rec_color = []
#     for item in items:
#         close_words = naive_keywords_search(all_embeddings, item)
#         closest_keywords.append(close_words)
#         # getting all the classes needed for a complete fashion set
#         for k, v in close_words.items():
#             if v[0] == "item":
#                 classes[v[1]] = True
#                 rec_class.append(list(map(lambda x: (x, k), v[2])))
#             elif v[0] == "color":
#                 rec_color.append(list(map(lambda x: (x, k), v[2])))
#     rec_class = flatten(rec_class)
#     rec_class.sort(reverse=True)
#     rec_color = flatten(rec_color)
#     rec_color.sort(reverse=True)
#     for rc in rec_class:
#         # remove item item if already preset in input outfit
#         if not classes[rc[0][3]]:
#             rec_class_.append(rc)
#
#     return {"item": rec_class_,
#             "color": rec_color}
#
#
# def phrase_rec(rec, limit=4):
#     def phrase_result(id, items):
#         ret = str(id + 1) + "."
#         for item in items:
#             ret += " " + item
#         return ret
#
#     def phrase_reason(recs, sims, inputs):
#         assert len(recs) == len(sims) == len(inputs)
#         rea = "Explanation: "
#         for j in range(len(recs)):
#             if recs[j] != "":
#                 rea += "'" + recs[j] + "' has similarity " + str(sims[j]) + " to keyword '" + inputs[j] + "';"
#         return rea
#
#     limit = min(limit, len(rec["item"]))
#     if len(rec["color"]) < len(rec["item"]):
#         print(rec["color"])
#         rec["color"] = rec["color"] + [(("", "", ""), "")] * (len(rec["item"]) - len(rec["color"]))
#         print(rec["color"])
#     for i in range(limit):
#         color_ = rec["color"][i]
#         class_ = rec["item"][i]
#         result = phrase_result(i, [color_[0][2], class_[0][2]])
#         reason = phrase_reason([color_[0][2], class_[0][2]],
#                                [color_[0][0], class_[0][0]],
#                                [color_[1], class_[1]]
#                                )
#         print(result)
#         print(reason)
#         print()
