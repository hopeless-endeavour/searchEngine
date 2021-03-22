import re
import math
import os
import datetime
import json
from collections import Counter

from  nltk.stem.snowball import FrenchStemmer

class Corpus():

    def __init__(self):

        self._documents = []
        self.doc_ids = []
        self.num_docs = 0
        self.vocab = []
        self.len_vocab = 0
        self._tf_matrix = []
        self._df_vec = []
        self._idf_vec = []
        self.tf_idf = []

    def add_document(self, id, title, text, flag):
        """ Creates and adds document objects into the _documents list """

        new_doc = Document(id, title, text)
        self._documents.append(new_doc)
        self.doc_ids.append(id)
        self.num_docs += 1
        if flag:
            self._update_vocab(id)
        

    def _update_vocab(self, doc_id):
        """ Adds any new words from the given document to the corpus vocab list """

        for i in self._documents:
            if i.id == doc_id:
                for j in i.tokens:
                    if j not in self.vocab:
                        self.vocab.append(j)

        self.vocab = sorted(self.vocab)
        self.len_vocab = len(self.vocab)

    def _calc_tf(self, doc):
        """ Calculates tf vector for a given document against the whole corpus vocab """

        tf = [0] * self.len_vocab
        for index, token in enumerate(self.vocab):
            for j in doc.tokens:
                if j == token:
                    tf[index] += 1

        for i in range(len(tf)):
            tf[i] = tf[i] / doc.num_tokens

        return tf

    def _calc_idf(self):
        """ Calculates idf vector for every word in the corpus vocab """

        # first calculate df
        self._df_vec = [0] * self.len_vocab
        for i, token in enumerate(self.vocab):
            for doc in self._documents:
                if token in doc.tokens:
                    self._df_vec[i] += 1

        # then calculate idf 
        self._idf_vec = [0] * self.len_vocab
        for i, df in enumerate(self._df_vec):
            self._idf_vec[i] = math.log(self.num_docs / (df))
        
        return 

    def calc_tfidf(self):
        """ Calculates the tf-idf matrix for the whole corpus """

        for i in self._documents:
            self._tf_matrix.append(self._calc_tf(i))

        self._calc_idf()

        for arr in self._tf_matrix:
            tfidf = []
            for i, tf in enumerate(arr):
                tfidf_value = tf * self._idf_vec[i]
                tfidf.append(tfidf_value)
            self.tf_idf.append(tfidf)

    def _calc_query_tfidf(self, query):
        """ Calculates the tf-idf of the query for every word in the corpus vocab. """

        q_tfidf = [0] * self.len_vocab
        counter = Counter(query.tokens)

        for token in query.tokens:

            tf = counter[token]/query.num_tokens
            df = 0
            try:
                index = self.vocab.index(token)
                df = self._df_vec[index]
            except:
                pass

            idf = math.log((self.num_docs+1)/(df+1))

            try:
                index = self.vocab.index(token)
                q_tfidf[index] = tf*idf
            except:
                pass

        return q_tfidf

    def _cosine_sim(self, vec1, vec2):
        """ Calculates the cosine similarity of two given vectors. """

        dot = sum(i*j for i, j in zip(vec1, vec2))
        magnitude = math.sqrt(
            sum([val**2 for val in vec1])) * math.sqrt(sum([val**2 for val in vec2]))
        if not magnitude:
            return 0

        return dot/magnitude

    def _compare_tfidfs(self, q_tfidf):
        """ Compates the tf-idf matrix of the corpus to that of the query. """

        comparison_vec = {}
        for i in range(len(self.tf_idf)):
            comparison_vec[i] = self._cosine_sim(q_tfidf, self.tf_idf[i])

        return comparison_vec

    def submit_query(self, query):
        """ Takes a query and calls all the appropriate methods to find the most similar _documents in the corpus """

        query = Query(query)
        q_tfidf = self._calc_query_tfidf(query)
        result = self._compare_tfidfs(q_tfidf)
        print(f"Similarity matrix: {result}")

        # if any results are 0, remove them 
        result = {x:y for x,y in result.items() if y != 0}

        
        doc_ids = []
        # sort the results by the highest similarity 
        res = sorted(result, key=result.get, reverse=True)
        print(res)
        # get the correct document ids of the resulting _documents 
        doc_ids = [self.doc_ids[i] for i in res]
        print(doc_ids)
        
        return doc_ids


class Document():

    def __init__(self, id, title, raw_text):

        self.id = id
        self.title = title
        if self.title:
            self.processed_title = self._preprocess(title, True)

        self.raw_text = raw_text
        self.clean_text = self._preprocess(raw_text, True)
        self.tokens = self._get_tokens()
        self.num_tokens = len(self.tokens)
        # self.cefr = self._cefr_score()

    def _remove_stopwords(self, text):
        """ Removes stopwords from given text. """

        with open("application/python_scripts/stop_words.txt", "r", encoding="utf-8") as f:
            stop_words = f.read().split("\n")[:-1]

        new_text = []
        for i in text:
            if i not in stop_words:
                new_text.append(i)

        return new_text

    def _preprocess(self, raw_text, flag):
        """ Parses given raw text. Returns a list of words. """

        self.stemmer = FrenchStemmer()

        punctuation = "!\"#$%&()*+…-.,/:;<=>?@[\\]^_«»{|}~\n“”€—–"
        clean_text = raw_text.lower()
        clean_text = re.sub('[%s]' % re.escape(
            punctuation), '', clean_text) # removes punctuation 
        clean_text = re.sub('\w*\d\w*', '', clean_text) # removes digits 
        clean_text = re.sub("'", ' ', clean_text) # replaces ' with space
        clean_text = re.sub('\n', '', clean_text) # removes carrage returns 
        clean_text = clean_text.split() # splits into an array of words 
        clean_text = [self.stemmer.stem(i) for i in clean_text]  # stems each word in array 

        if flag:
            return self._remove_stopwords(clean_text)

        else:
            return clean_text

    def _get_tokens(self):
        """ Gets all the individual words/tokens from the objects title and text. Returns list of tokens.  """

        tokens = []

        if self.title:
            for i in self.processed_title:
                tokens.append(i)

        for i in self.clean_text:
                tokens.append(i)
        
        return tokens


class Query(Document):
    def __init__(self, query):
        # give queries an id? Keep track of user queries?
        # initialise query from parent document, but without title or id 
        super().__init__(id=None, title=None, raw_text=query)

    def spell_check(self):
        pass
