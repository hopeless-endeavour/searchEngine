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

        new_doc = Document(id, title, text)
        self.documents.append(new_doc)
        self.doc_ids.append(id)
        self.num_docs += 1
        if flag:
            self._update_vocab(id)
        

    def _update_vocab(self, doc_id):

        for i in self.documents:
            if i.id == doc_id:
                for j in i.tokens:
                    if j not in self.vocab:
                        self.vocab.append(j)

        self.vocab = sorted(self.vocab)
        self.len_vocab = len(self.vocab)

    def _calc_tf(self, doc):

        tf = [0] * self.len_vocab
        for index, token in enumerate(self.vocab):
            for j in doc.tokens:
                if j == token:
                    tf[index] += 1

        for i in range(len(tf)):
            tf[i] = tf[i] / doc.num_tokens

        return tf

    def _calc_idf(self):

        df = [0] * self.len_vocab
        for i, token in enumerate(self.vocab):
            for doc in self.documents:
                if token in doc.tokens:
                    df[i] += 1

        self.df_vec = df

        idf = [0] * self.len_vocab
        for i, df in enumerate(df):
            idf[i] = math.log(self.num_docs / (df))
        
        self.idf_vec = idf

    def calc_tfidf(self):

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
        dot = sum(i*j for i, j in zip(vec1, vec2))
        magnitude = math.sqrt(
            sum([val**2 for val in vec1])) * math.sqrt(sum([val**2 for val in vec2]))
        if not magnitude:
            return 0

        return dot/magnitude

    def _compare_tfidfs(self, q_tfidf):

        comparison_vec = {}
        for i in range(len(self.tf_idf)):
            comparison_vec[i] = self._cosine_sim(q_tfidf, self.tf_idf[i])

        return comparison_vec

    def submit_query(self, query):

        query = Query(query)
        q_tfidf = self._calc_query_tfidf(query)
        result = self._compare_tfidfs(q_tfidf)
        print(result)
        result = {x:y for x,y in result.items() if y != 0}

        # TODO: even when both texts contain the word, both come up with 0, work out way to see if there are no matches
        # TODO: dataset scrapes whole page, so results come up if theres a refereenced article to another page with a teaser

        doc_ids = []
        res = sorted(result, key=result.get, reverse=True)
        doc_ids = [self.doc_ids[i] for i in res]
        
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
        with open("application/python_scripts/stop_words.txt", "r", encoding="utf-8") as f:
            stop_words = f.read().split("\n")[:-1]

        new_text = []
        for i in text:
            if i not in stop_words:
                new_text.append(i)

        return new_text

    def _preprocess(self, raw_text):

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
        super().__init__(id=None, title=None, raw_text=query)

    def spell_check(self):
        pass


# c = Corpus()
# c.add_document(1, 'situation de la gouvernement', text, True)
# c.add_document(2, 'situation des musulmans', text2, True)
# c.add_document(3, 'Donald Trump', text3, True)
# c.calc_tfidf()
# res = c.submit_query("macron")
