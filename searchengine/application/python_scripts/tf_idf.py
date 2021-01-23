import re
import math
import os
import datetime
import json
from collections import Counter

from  nltk.stem.snowball import FrenchStemmer

text = "Le gouvernement va pouvoir continuer de mettre en place des restrictions pour faire face à la deuxième vague de coronavirus. Dans une ambiance souvent tendue, l’Assemblée nationale a voté samedi la prorogation de l’état d’urgence sanitaire jusqu’au 16 février. Le projet de loi, voté par 71 voix contre 35 en première lecture, est attendu au Sénat mercredi et devrait être adopté définitivement début novembre."

text2 = "Les appels au boycott de produits français se sont multipliés samedi dans plusieurs pays du Moyen-Orient. L’Organisation de coopération islamique, qui réunit les pays musulmans, a déploré « les propos de certains responsable français susceptibles de nuire aux relations franco-musulmanes ». L’émoi a été suscité par les propos du président Emmanuel Macron, qui a promis de ne pas « renoncer aux caricatures » de Mahomet, interdites dans la religion musulmane. vague"

text3 = "Cette année, Joe Biden a renvoyé Donald Trump dans son golf privé en prenant bientôt sa place à la Maison Blanche. L’Argentine est proche de légaliser l’avortement et Adèle Haenel s’est levée contre les violences faites aux femmes. Pour la première fois dans l’Union européenne, les énergies renouvelables ont produit plus d’électricité que les combustibles fossiles lors du premier semestre 2020. Tom Moor, un ancien capitaine de l'armée britannique centenaire a collecté près de 40 millions de livres pour le système hospitalier du Royaume-Uni, en marchant avec son déambulateur !"

class Corpus():

    def __init__(self):

        self.documents = []
        self.doc_ids = []
        self.num_docs = 0
        self.vocab = []
        self.len_vocab = 0
        self.tf_matrix = []
        self.df_vec = []
        self.idf_vec = []
        self.tf_idf = []

    def add_document(self, id, title, text, flag):
        """ Creates and adds document objects into the documents list """

        new_doc = Document(id, title, text)
        self.documents.append(new_doc)
        self.doc_ids.append(id)
        self.num_docs += 1
        if flag:
            self._update_vocab(id)
        

    def _update_vocab(self, doc_id):
        """ Adds any new words from the given document to the corpus vocab list """

        for i in self.documents:
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
        self.df_vec = [0] * self.len_vocab
        for i, token in enumerate(self.vocab):
            for doc in self.documents:
                if token in doc.tokens:
                    self.df_vec[i] += 1

        # then calculate idf 
        self.idf_vec = [0] * self.len_vocab
        for i, df in enumerate(self.df_vec):
            self.idf_vec[i] = math.log(self.num_docs / (df))
        
        return 

    def calc_tfidf(self):
        """ Calculates the tf-idf matrix for the whole corpus """

        for i in self.documents:
            self.tf_matrix.append(self._calc_tf(i))

        self._calc_idf()

        for arr in self.tf_matrix:
            tfidf = []
            for i, tf in enumerate(arr):
                tfidf_value = tf * self.idf_vec[i]
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
                df = self.df_vec[index]
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
        """ Takes a query and calls all the appropriate methods to find the most similar documents in the corpus """

        query = Query(query)
        q_tfidf = self._calc_query_tfidf(query)
        result = self._compare_tfidfs(q_tfidf)
        print(f"Similarity matrix: {result}")

        # if any results are 0, remove them 
        result = {x:y for x,y in result.items() if y != 0}

        # TODO: even when both texts contain the word, both come up with 0, work out way to see if there are no matches
        # TODO: dataset scrapes whole page, so results come up if theres a refereenced article to another page with a teaser
        
        doc_ids = []
        # sort the results by the highest similarity 
        res = sorted(result, key=result.get, reverse=True)
        print(res)
        # get the correct document ids of the resulting documents 
        doc_ids = [self.doc_ids[i] for i in res]
        print(doc_ids)
        
        return doc_ids


class Document():

    def __init__(self, id, title, raw_text):

        self.id = id
        self.title = title
        if self.title:
            self.processed_title = self._preprocess(title)

        self.raw_text = raw_text
        self.clean_text = self._preprocess(raw_text)
        self.tokens = self._get_tokens()
        self.num_tokens = len(self.tokens)

    def _remove_stopwords(self, text):
        """ Removes stopwords from given text. """

        with open("application/python_scripts/stop_words.txt", "r", encoding="utf-8") as f:
            stop_words = f.read().split("\n")[:-1]

        new_text = []
        for i in text:
            if i not in stop_words:
                new_text.append(i)

        return new_text

    def _preprocess(self, raw_text):
        """ Parses given raw text. Returns a list of words. """

        stemmer = FrenchStemmer()

        punctuation = "!\"#$%&()*+…-.,/:;<=>?@[\\]^_«»{|}~\n“”€—–"
        clean_text = raw_text.lower()
        clean_text = re.sub('[%s]' % re.escape(
            punctuation), '', clean_text)
        clean_text = re.sub('\w*\d\w*', '', clean_text)
        # replaces ' with space
        clean_text = re.sub("'", ' ', clean_text)
        clean_text = re.sub('\n', '', clean_text)
        clean_text = clean_text.split()
        clean_text = [stemmer.stem(i) for i in clean_text]

        return self._remove_stopwords(clean_text)

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


# c = Corpus()
# c.add_document(1, 'situation de la gouvernement', text, True)
# c.add_document(2, 'situation des musulmans', text2, True)
# c.add_document(3, 'Donald Trump', text3, True)
# c.calc_tfidf()
# res = c.submit_query("macron")
