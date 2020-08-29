import re
import unicodedata

import pandas as pd

from nltk import LancasterStemmer
from nltk.corpus import stopwords
from fAshIon.Utils import get_ontology_def
from nltk.stem.wordnet import WordNetLemmatizer


def preprocess_data(vocabs):
    """
    Preprocess text
    :param vocabs: list of word tokens
    :return: processed list of word tokens
    """
    def remove_non_ascii(words):
        """Remove non-ASCII characters from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode("utf-8", "ignore")
            new_words.append(new_word)
        return new_words

    def to_lowercase(words):
        """Convert all characters to lowercase from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = word.lower()
            new_words.append(new_word)
        return new_words

    def remove_punctuation(words):
        """Remove punctuation from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = re.sub(r"[^\w\s]", "", word)
            if new_word != "":
                new_words.append(new_word)
        return new_words

    def remove_stopwords(words):
        """Remove stop words from list of tokenized words"""
        new_words = []
        for word in words:
            if word not in stopwords.words("english"):
                new_words.append(word)
        return new_words

    def stem_words(words):
        """Stem words in list of tokenized words"""
        stemmer = LancasterStemmer()
        stems = []
        for word in words:
            stem = stemmer.stem(word)
            stems.append(stem)
        return stems

    def lemmatize(words):
        """Lemmatize verbs in list of tokenized words"""
        lemmatizer = WordNetLemmatizer()
        lemmas = []
        for word in words:
            lemma = lemmatizer.lemmatize(word)
            lemmas.append(lemma)
        return lemmas

    def numbering_words(words):
        number = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        ret = []
        for word in words:
            if word[0] not in number:
                ret.append(word)
        return ret

    def ontology_lemma(words):
        ret = []
        for word in words:
            if word == "knit":
                ret.append("knitwear")
            elif word == "bralet" or word == "bralette":
                ret.append("bra")
            elif word == "sunglass":
                ret.append("sunglasses")
            elif word == "glass":
                ret.append("glasses")
            elif word == "hood":
                ret.append("hoodie")
            else:
                ret.append(word)
        return ret

    vocabs = to_lowercase(vocabs)
    vocabs = remove_non_ascii(vocabs)
    vocabs = remove_punctuation(vocabs)
    vocabs = remove_stopwords(vocabs)
    # vocabs = stem_words(vocabs)
    vocabs = lemmatize(vocabs)
    vocabs = numbering_words(vocabs)
    vocabs = ontology_lemma(vocabs)
    return vocabs


def add_ontology(dataframe):
    """
    Add ontology-related columns to dataframe
    :param dataframe: input dataframe with raw data
    :return: dataframe with ontology columns
    """
    # loaded custom ontology framework
    onto_def = get_ontology_def()
    # getting ontology attributes, remove last element in definition as
    # context should always be the last element and is not needed as attributes
    onto_attr = onto_def["def"][0: len(onto_def["def"]) - 1]

    # helper function to populate ontology columns
    # noinspection PyShadowingNames
    def ontology_processing(onto_attr, onto_def, tokenized_description):
        ret_ = {}
        for attr in onto_attr:
            ret_[attr] = []
        for word in tokenized_description:
            for attr in onto_attr:
                if word in onto_def[attr]:
                    ret_[attr].append(word)
                    break
        ret_ = [v for k, v in ret_.items()]
        return pd.Series(ret_, index=onto_attr)

    onto_df = dataframe[["s_id", "dup_score", "i_name"]]
    onto_df[onto_attr] = onto_df["i_name"].apply(lambda x: ontology_processing(onto_attr, onto_def, x))
    return onto_df
