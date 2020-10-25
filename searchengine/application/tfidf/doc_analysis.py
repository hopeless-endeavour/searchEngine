import os
import re
import json
import math
import numpy as np
from collections import Counter
import requests


def checkUrl(url):
    req = requests.head(url)
    if req.status_code != 200:
        return (f'Error. Status code: {req.status_code}')
    else:
        return True


def readData(path):
    """ Returns 2D array as [[title, text, url], [title2, text2, url2]]"""

    corpus = []

    for i in os.listdir(path=path):
        with open(f'{path}/{i}','r', encoding="utf8") as f:
            full_data = f.read()
            json_obj = json.loads(full_data)
        
            if (json_obj['text'] != " ") :
                corpus.append([json_obj['title'], json_obj['text'], json_obj['url']])

    return corpus


def removeStopwords(text):
    with open("application/tfidf/stop_words.txt", "r", encoding="utf-8") as f:
        stop_words = f.read().split("\n")[:-1]

    new_text = []
    for i in text:
        if i not in stop_words:
            new_text.append(i)

    return new_text

def preProcess(text):
    """ Tokenizes text, makes lowercase, removes punctuation, non-sensical
    text, digits and stop words. """

    punctuation = "!\"#$%&()*+…-.,/:;<=>?@[\\]^_«»{|}~\n“”€—–"
    text = text.lower()
    text = re.sub('[%s]' % re.escape(punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub("'", ' ', text) # replaces ' with space
    text = re.sub('\n', '', text)
    text = text.split()
    text = removeStopwords(text)

    return text

def get_vocab(data):
    """ Takes corpus where each document is a list of all their words.
        Returns a unique vocab dict of the whole corpus. """

    unique_words = set()
    vocab = {}

    for text in data:
        for word in text:
            unique_words.add(word)

    for i, word in enumerate(sorted(unique_words)):
        vocab[i] = word

    return vocab

def calcTF(doc, vocab):
    """ Calculates TF for each text. Returns dict where keys are unique words and
    values are their corresponding TF (= num of times term appears in document /
    total num of terms in document)"""

    # calcs num of times every word in the vocab appears in the doc as vector
    tf = [0] * len(vocab)
    for key, value in vocab.items():
        for term in doc:
            if term == value:
                tf[key] += 1

    calcs tf for each word
    for i in tf:
        tf[i] = tf[i] / len(text)

    return tf


# def calcIDF(data, df):
#     idf = {}
#     for word in df:
#         idf[word] = math.log(len(data['text']) / df[word])

#     return idf

def idf(corpus, vocab):

    df = [0] * len(vocab)
    for i, word in enumerate(vocab.values()):
        for doc in corpus:
            if word in doc:
                df[i] += 1

    idf = [0]*len(vocab)
    for i, value in enumerate(df):
        idf[i] = math.log(len(corpus) / (1 + df[i]))

    return idf

def cos_sim(vec1, vec2):
    cos = np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))
    return cos

def calc_query_vec(query, vocab, clean_corpus):

    Q = [0] * len(vocab)

    counter = Counter(query)
    words_count = len(query)

    query_weights = {}

    for token in np.unique(query):

        tf = counter[token]/words_count
        df = 0
        for i, word in enumerate(vocab.values()):
            for doc in clean_corpus:
                if word in doc:
                    df += 1
        idf = math.log((len(clean_corpus)+1)/(df+1))

        try:
            for key, value in vocab.items():
                if token == value:
                    ind = key
            Q[ind] = tf*idf
        except:
            pass
    return Q

def calc_cos_sim(query, vocab, tfidf, clean_corpus):

    clean_query = preProcess(query)
    query_vec = calc_query_vec(clean_query, vocab, clean_corpus)
    d_cosines = []

    for vec in tfidf:
        d_cosines.append(cos_sim(query_vec,vec))

    out = np.array(d_cosines).argsort()

    return out, d_cosines


def tf_idf(query, corpus, num=1):

    texts = [corpus[i][1] for i in range(len(corpus))]
    clean_corpus = [preProcess(i) for i in texts]
    vocab = get_vocab(clean_corpus)
    tf_vec = []

    for i in clean_corpus:
        tf_vec.append(calcTF(i,vocab))

    tf_vec = np.array(tf_vec)
    idf_vec = idf(clean_corpus, vocab)

    diag_idf = np.diag(idf_vec)
    tf_idf = np.matmul(tf_vec, diag_idf)
    norm_tfidf = []
    for i in tf_idf:
        norm_tfidf.append(i/np.linalg.norm(i,2))

    results = calc_cos_sim(query, vocab, norm_tfidf, clean_corpus)[0][:num]

    top_texts = []
    for i in results:
        result = {}
        result['title'] = corpus[i][0]
        result['text'] = corpus[i][1][:200]
        result['url'] = corpus[i][2]
        top_texts.append(result)

    result_dict = dict(zip(results,top_texts))

    return top_texts

