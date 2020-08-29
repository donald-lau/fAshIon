import os
import datetime
import pprint
from os.path import dirname, normpath, join

import math

import numpy as np
import tensorflow as tf

from random import shuffle
from six.moves import xrange
from tempfile import gettempdir
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.contrib.tensorboard.plugins import projector
from fAshIon.Utils import flatten, get_word_idx_dict, get_ontology_def, dump_output_file, phrase_model_id

data_index = 0


# ++++++ Build graph for learned word embedding ++++++
def skipgram_clustering(df, onto_attr, model_id, epochs=500001):
    """
    using neural network model to build topic modelling cluster on topics in onto_attr with data in df
    :param df: dataframe with training data
    :param onto_attr: list of ontology attributes to be learned
    :param model_id: id for the learned cluster
    :param epochs: number of epochs the NN will run to learn the clustering
    :return: dictionary of vocabs, model id and learned embeddings for each word
    """

    # phrase skipgram for the given tokenized description input
    # noinspection PyShadowingNames
    def phrase_skipgram(tokenized_description, word2idx):
        if len(tokenized_description) < 2:
            return []
        skipgram = []
        shuffle(tokenized_description)
        for i in range(len(tokenized_description)):
            for window in range(-2, 2):
                if len(tokenized_description) > (i + window) >= 0 != window:
                    target = word2idx[tokenized_description[i]]
                    context = word2idx[tokenized_description[i + window]]
                    # target = tokenized_description[i]
                    # context = tokenized_description[i + window]
                    skipgram.append((target, context))
        return skipgram

    # Phrase skipgram multiple times depending on corresponding duplicate score
    def phrase_skipgram_dup(row):
        skipgram = []
        for _ in range(int(row["dup_score"]) + 1):
            skipgram.append(phrase_skipgram(row["ontology"], word2idx))
        return flatten(skipgram)

    word2idx, idx2word = get_word_idx_dict(onto_attr)
    # add skipgram to "ontology" column
    sg_df = df.copy()
    sg_df["ontology"] = sg_df[onto_attr].values.tolist()
    sg_df["ontology"] = sg_df["ontology"].apply(lambda x: flatten(x))
    sg_df["ontology"] = sg_df.apply(lambda row: phrase_skipgram_dup(row), axis=1)
    input_target_pairs = sg_df["ontology"].tolist()
    input_target_pairs = flatten(input_target_pairs)
    inputs, targets = zip(*input_target_pairs)

    # generate training batch for the skip-gram model
    # noinspection PyShadowingNames
    def generate_batch(batch_size):
        global data_index
        # get the batch_size windows of inputs and targets pair
        if data_index + batch_size <= len(inputs):
            batch = np.array(inputs[data_index: data_index + batch_size])
            labels = np.array(targets[data_index: data_index + batch_size]).reshape((batch_size, 1))
            data_index += batch_size
        # wrap around the end and concat from the beginning of the dataset
        else:
            shift = (data_index + batch_size) % len(inputs)
            batch = np.array(inputs[data_index: len(inputs)])
            batch = np.append(batch, inputs[0: shift])
            labels = np.array(targets[data_index: len(inputs)])
            # print(data_index)
            # print(shift)
            # print(labels.shape)
            # print("==================")
            labels = (np.append(labels, targets[0: shift])).reshape((batch_size, 1))
            data_index = shift
        return batch, labels

    # Building the graph
    print("======Start building graph======")
    batch_size = 128
    embedding_size = 128  # Dimension of the embedding vector.
    num_sampled = 64  # Number of negative examples to sample.
    vocabulary_size = len(word2idx)

    # We pick a random validation set to sample nearest neighbors. Here we limit
    # the validation samples to the words that have a low numeric ID, which by
    # construction are also the most frequent. These 3 variables are used only for
    # displaying model accuracy, they don"t affect calculation.
    valid_size = 16  # Random set of words to evaluate similarity on.
    valid_window = min(60, int(len(word2idx) / 2))  # Only pick dev samples in the head of the distribution.
    valid_examples = np.random.choice(valid_window, valid_size, replace=False)

    graph = tf.Graph()

    with graph.as_default():

        # Input data.
        with tf.name_scope("inputs"):
            train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
            train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
            valid_dataset = tf.constant(valid_examples, dtype=tf.int32)

        # Ops and variables pinned to the CPU because of missing GPU implementation
        with tf.device("/cpu:0"):
            # Look up embeddings for inputs.
            with tf.name_scope("embeddings"):
                embeddings = tf.Variable(
                    tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
                embed = tf.nn.embedding_lookup(embeddings, train_inputs)

            # Construct the variables for the NCE loss
            with tf.name_scope("weights"):
                nce_weights = tf.Variable(
                    tf.truncated_normal([vocabulary_size, embedding_size],
                                        stddev=1.0 / math.sqrt(embedding_size)))
            with tf.name_scope("biases"):
                nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

        # Compute the average NCE loss for the batch.
        # tf.nce_loss automatically draws a new sample of the negative labels each
        # time we evaluate the loss.
        # Explanation of the meaning of NCE loss:
        #   http://mccormickml.com/2016/04/19/word2vec-tutorial-the-skip-gram-model/
        with tf.name_scope("loss"):
            loss = tf.reduce_mean(
                tf.nn.nce_loss(
                    weights=nce_weights,
                    biases=nce_biases,
                    labels=train_labels,
                    inputs=embed,
                    num_sampled=num_sampled,
                    num_classes=vocabulary_size))

        # Add the loss value as a scalar to summary.
        tf.summary.scalar("loss", loss)

        # Construct the SGD optimizer using a learning rate of 1.0.
        with tf.name_scope("optimizer"):
            optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)

        # Compute the cosine similarity between minibatch examples and all
        # embeddings.
        norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keepdims=True))
        normalized_embeddings = embeddings / norm
        valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings,
                                                  valid_dataset)
        similarity = tf.matmul(
            valid_embeddings, normalized_embeddings, transpose_b=True)

        # Merge all summaries.
        merged = tf.summary.merge_all()

        # Add variable initializer.
        init = tf.global_variables_initializer()

        # Create a saver.
        saver = tf.train.Saver()

    # Begin training
    with tf.Session(graph=graph) as session:
        log_dir = "./model_log/" + model_id + "/"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        # Open a writer to write summaries.
        writer = tf.summary.FileWriter(log_dir, session.graph)

        # We must initialize all variables before we use them.
        init.run()
        print("Initialized")

        average_loss = 0
        for epoch in range(epochs):
            batch_inputs, batch_labels = generate_batch(batch_size)
            feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}

            # Define metadata variable.
            run_metadata = tf.RunMetadata()

            # We perform one update step by evaluating the optimizer op (including it
            # in the list of returned values for session.run()
            # Also, evaluate the merged op to get all summaries from the returned
            # "summary" variable. Feed metadata variable to session for visualizing
            # the graph in TensorBoard.
            _, summary, loss_val = session.run([optimizer, merged, loss],
                                               feed_dict=feed_dict,
                                               run_metadata=run_metadata)
            average_loss += loss_val

            # Add returned summaries to writer in each step.
            writer.add_summary(summary, epoch)
            # Add metadata to visualize the graph for the last run.
            if epoch == (epochs - 1):
                writer.add_run_metadata(run_metadata, "step%d" % epoch)

            if epoch % 100000 == 0:
                if epoch > 0:
                    average_loss /= 2000
                # The average loss is an estimate of the loss over the last 2000
                # batches.
                print("Average loss at step ", epoch, ": ", average_loss)
                average_loss = 0

            # Note that this is expensive (~20% slowdown if computed every 500 steps)
            if epoch % 200000 == 0:
                sim = similarity.eval()
                for i in xrange(valid_size):
                    valid_word = idx2word[valid_examples[i]]
                    top_k = 8  # number of nearest neighbors
                    nearest = (-sim[i, :]).argsort()[1:top_k + 1]
                    log_str = "Nearest to %s:" % valid_word
                    for k in xrange(top_k):
                        if nearest[k] < vocabulary_size:
                            close_word = idx2word[nearest[k]]
                        else:
                            close_word = "unknown (hotfix)"
                        log_str = "%s %s," % (log_str, close_word)
                    print(log_str)
        final_embeddings = normalized_embeddings.eval()

        # Write corresponding labels for the embeddings.
        with open(log_dir + "/metadata.tsv", "w") as f:
            for i in range(vocabulary_size):
                f.write(idx2word[i] + "\n")

        # Save the model for checkpoints.
        saver.save(session, os.path.join(log_dir, model_id))
        print("==============================saved model checkpoint==============================")

        # Create a configuration for visualizing embeddings with the labels in
        # TensorBoard.
        config = projector.ProjectorConfig()
        embedding_conf = config.embeddings.add()
        embedding_conf.tensor_name = embeddings.name
        embedding_conf.metadata_path = os.path.join(log_dir, "metadata.tsv")
        projector.visualize_embeddings(writer, config)

    writer.close()

    # Visualize the graph
    # Function to draw visualization of distance between embeddings.
    # noinspection PyShadowingNames
    def plot_with_labels(low_dim_embs, labels, filename):
        assert low_dim_embs.shape[0] >= len(labels), "More labels than embeddings"
        plt.figure(figsize=(18, 18))  # in inches
        for i, label in enumerate(labels):
            x, y = low_dim_embs[i, :]
            plt.scatter(x, y)
            plt.annotate(
                label,
                xy=(x, y),
                xytext=(5, 2),
                textcoords="offset points",
                ha="right",
                va="bottom")
        plt.title(model_id)
        plt.savefig(filename)
        plt.show()

    try:
        print("Generating graph")
        # pylint: disable=g-import-not-at-top
        from sklearn.manifold import TSNE
        import matplotlib.pyplot as plt

        tsne = TSNE(
            perplexity=30, n_components=2, init="pca", n_iter=5000, method="exact")
        plot_only = min(500, len(idx2word))
        low_dim_embs = tsne.fit_transform(final_embeddings[:plot_only, :])
        labels = [idx2word[i] for i in range(plot_only)]
        # out_dir = normpath(join(dirname(dirname(__file__)), "/output/graph", str(model_id) + ".png"))
        out_dir = os.path.join(gettempdir(), 'tsne.png')
        plot_with_labels(low_dim_embs, labels, out_dir)
        print("Out dir: " + str(out_dir))
        return {"model_id": model_id,
                "labels": labels,
                "low_embeds": low_dim_embs,
                "final_embeds": final_embeddings}

    except ImportError as ex:
        print("Please install sklearn, matplotlib, and scipy to show embeddings.")
        print(ex)

    print("End of function")


def get_cluster_dict(cluster, onto_attrs):
    """
    return dictionary for ontology keywords in cluster and corresponding id,
    note this id is within the input cluster and different from the id in ontology definition
    :param cluster: cluster for learned topic modelling
    :param onto_attrs: list of ontology attributes in the cluster
    :return: lookup and reverse lookup dictionary
    """
    onto_def = get_ontology_def()
    dict_ = {}
    rev_dict_ = {}
    for attr in onto_attrs:
        vocabs = enumerate(cluster["labels"])
        attr_dict = {}
        for i, k in vocabs:
            if k in onto_def[attr]:
                attr_dict[k] = i
        dict_[attr] = attr_dict
        rev_dict_[attr] = {v: k for i, (k, v) in enumerate(attr_dict.items())}
    return dict_, rev_dict_


def build_sims_matrix(cluster, onto_attrs):
    """
    build a similarity matrix based on cosine distance for same space or 2 spaces cluster,
    for 3 spaces cluster a normalized similarity is stored as value in a 3d matrix
    :param cluster: cluster for learned topic modelling
    :param onto_attrs: list of ontology attributes in the cluster
    :return: the similarity matrix
    """

    def cosine_similarity_three_vec(v1, v2, v3):
        norma = normalize(v1)
        normb = normalize(v2)
        normc = normalize(v3)
        return cosine_similarity(norma, normb) + \
            cosine_similarity(norma, normc) + \
            cosine_similarity(normb, normc)

    # avoiding multi-layer look up to improve performance
    # noinspection PyShadowingNames
    def get_onto_id_embeddings_pair(attr_id, onto_def):
        onto_word2idx = onto_def[onto_attrs[attr_id]]
        onto_word2idx = {k: v[0] for i, (k, v) in enumerate(onto_word2idx.items())}
        cluster_word2idx, cluster_idx2word = get_cluster_dict(cluster, onto_attrs)
        cluster_word2idx, cluster_idx2word \
            = cluster_word2idx[onto_attrs[attr_id]], cluster_idx2word[onto_attrs[attr_id]]
        # avoiding multi-layer look up to improve performance
        onto_id_embeddings_pairs = [(onto_word2idx[key],
                                     (embeddings[cluster_word2idx[key]]).reshape(1, embedding_size))
                                    for key in onto_word2idx]
        return onto_id_embeddings_pairs

    onto_def = get_ontology_def()
    init_val = -10
    embeddings = cluster["final_embeds"]
    embedding_size = len(embeddings[0])
    print("Start building matrix " + phrase_model_id(onto_attrs, "_matrix"))
    print(datetime.datetime.now())
    # 2d matrix with ontology in same space
    if len(onto_attrs) == 1:
        # max_id defines the return matrix dimensions
        max_id = int(onto_def["max_ids"][onto_attrs[0]])
        onto_id_embeddings_pairs = get_onto_id_embeddings_pair(0, onto_def)
        matrix = np.full((max_id, max_id), init_val, dtype=np.float)
        sims_matrix = None
        for onto_id_1, embeddings_1 in onto_id_embeddings_pairs:
            for onto_id_2, embeddings_2 in onto_id_embeddings_pairs:
                if matrix[onto_id_1][onto_id_2] == init_val:
                    sims = cosine_similarity(embeddings_1, embeddings_2)[0][0]
                    matrix[onto_id_1][onto_id_2] = sims
                    matrix[onto_id_2][onto_id_1] = sims
            sims_matrix = {"matrix": matrix, "axis1": onto_attrs[0], "axis2": onto_attrs[0]}
            dump_output_file(sims_matrix, phrase_model_id(onto_attrs, "_matrix"), "fAshIon/output/matrix")
        return sims_matrix

    # 2d matrix with ontology in different spaces
    elif len(onto_attrs) == 2:
        # max_id defines the return matrix dimensions
        max_id_1 = int(onto_def["max_ids"][onto_attrs[0]])
        max_id_2 = int(onto_def["max_ids"][onto_attrs[1]])
        onto_id_embeddings_pairs_1 = get_onto_id_embeddings_pair(0, onto_def)
        onto_id_embeddings_pairs_2 = get_onto_id_embeddings_pair(1, onto_def)
        matrix = np.full((max_id_1, max_id_2), init_val, dtype=np.float)
        sims_matrix = None
        for onto_id_1, embeddings_1 in onto_id_embeddings_pairs_1:
            for onto_id_2, embeddings_2 in onto_id_embeddings_pairs_2:
                sims = cosine_similarity(embeddings_1, embeddings_2)[0][0]
                matrix[onto_id_1][onto_id_2] = sims
            sims_matrix = {"matrix": matrix, "axis1": onto_attrs[0], "axis2": onto_attrs[1]}
            dump_output_file(sims_matrix, phrase_model_id(onto_attrs, "_matrix"), "fAshIon/output/matrix")
            print(datetime.datetime.now())
        return sims_matrix

    # 3d matrix with ontology in 3 different spaces
    elif len(onto_attrs) == 3:
        max_id_1 = int(onto_def["max_ids"][onto_attrs[0]])
        max_id_2 = int(onto_def["max_ids"][onto_attrs[1]])
        max_id_3 = int(onto_def["max_ids"][onto_attrs[2]])

        onto_id_embeddings_pairs_1 = get_onto_id_embeddings_pair(0, onto_def)
        onto_id_embeddings_pairs_2 = get_onto_id_embeddings_pair(1, onto_def)
        onto_id_embeddings_pairs_3 = get_onto_id_embeddings_pair(2, onto_def)
        matrix = np.full((max_id_1, max_id_2, max_id_3), init_val, dtype=np.float)

        sims_matrix = None
        for onto_id_1, embeddings_1 in onto_id_embeddings_pairs_1:
            for onto_id_2, embeddings_2 in onto_id_embeddings_pairs_2:
                for onto_id_3, embeddings_3 in onto_id_embeddings_pairs_3:
                    sims = cosine_similarity_three_vec(embeddings_1, embeddings_2, embeddings_3)[0][0]
                    matrix[onto_id_1][onto_id_2][onto_id_3] = sims
            sims_matrix = {"matrix": matrix, "axis1": onto_attrs[0], "axis2": onto_attrs[1], "axis3": onto_attrs[2]}
            dump_output_file(sims_matrix, phrase_model_id(onto_attrs, "_matrix"), "fAshIon/output/matrix")
            print(datetime.datetime.now())
        return sims_matrix
