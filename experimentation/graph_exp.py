import re
import math
from collections import Counter

text = "Le gouvernement va pouvoir continuer de mettre en place des restrictions pour faire face à la deuxième vague de coronavirus. Dans une ambiance souvent tendue, l’Assemblée nationale a voté samedi la prorogation de l’état d’urgence sanitaire jusqu’au 16 février. Le projet de loi, voté par 71 voix contre 35 en première lecture, est attendu au Sénat mercredi et devrait être adopté définitivement début novembre."

text2 = "Les appels au boycott de produits français se sont multipliés samedi dans plusieurs pays du Moyen-Orient. L’Organisation de coopération islamique, qui réunit les pays musulmans, a déploré « les propos de certains responsable français susceptibles de nuire aux relations franco-musulmanes ». L’émoi a été suscité par les propos du président Emmanuel Macron, qui a promis de ne pas « renoncer aux caricatures » de Mahomet, interdites dans la religion musulmane."

class Corpus():
    
    def __init__(self):
        
        self.documents = {}
        self.num_docs = 0
        self.vocab = []
        self.len_vocab = 0
        self.tf_matrix = []
        self.df_vec = []
        self.idf_vec = []
        self.tf_idf = []


    def add_document(self, name, text):
        
        new_doc = Document(name, text)
        self.documents[self.num_docs] = new_doc # using num_docs as id for new doc
        self.update_vocab(self.num_docs)
        self.num_docs += 1
        

    def update_vocab(self, doc_index):

        for i in self.documents[doc_index].tokens:
            if i not in self.vocab:
                self.vocab.append(i)

        self.vocab = sorted(self.vocab)       
        self.len_vocab = len(self.vocab)
        

    def calc_tf(self, doc):
        
        tf = [0] * self.len_vocab
        for index, token in enumerate(self.vocab):
            for j in doc.tokens:
                if j == token:
                    tf[index] += 1

        for i in range(len(tf)):
            tf[i] = tf[i] / doc.num_tokens

        return tf
        
                    
    def calc_idf(self):

        df = [0] * self.len_vocab
        for i, token in enumerate(self.vocab):
            for doc in self.documents:
                if token in self.documents[doc].tokens:
                    df[i] += 1

        self.df_vec = df  

        idf = [0] * self.len_vocab
        for i, df in enumerate(df):
            idf[i] = math.log(self.num_docs / (df))

        return idf


    def calc_tfidf(self):

        self.tf_matrix = []

        for i in self.documents.values():
            self.tf_matrix.append(self.calc_tf(i))

        self.idf_vec = []
        self.idf_vec = self.calc_idf()

        for arr in self.tf_matrix:
            tfidf = []    
            for i, tf in enumerate(arr):
                tfidf_value = tf * self.idf_vec[i]
                tfidf.append(tfidf_value)
            self.tf_idf.append(tfidf)

    def get_query_tfidf(self, query):

        q_tfidf = [0] * self.len_vocab
        counter = Counter(query.tokens)
        
        for token in query.tokens:

            tf = counter[token]/query.num_tokens
            df = 0
            try:
                index = self.vocab.index(token)
                df = self.df[index]
            except:
                pass

            idf = math.log((self.num_docs+1)/(df+1))

            try:
                index = self.vocab.index(token)
                q_tfidf[index] = tf*idf
            except:
                pass
        
        return q_tfidf

    
    def cosine_sim(self, vec1, vec2):
        dot = sum(i*j for i,j in zip(vec1, vec2))
        magnitude = math.sqrt(sum([val**2 for val in vec1])) * math.sqrt(sum([val**2 for val in vec2]))
        if not magnitude:
            return 0

        return dot/magnitude


    def compare_tfidfs(self, q_tfidf):

        comparison_vec = []
        for i in self.tf_idf:
            comparison_vec.append(self.cosine_sim(q_tfidf, i))

        return comparison_vec

    def search_query(self, query):

        query = Query(query)
        q_tfidf = self.get_query_tfidf(query)
        result = self.compare_tfidfs(q_tfidf)
        
        return sorted(result, reverse=True)
   
        
class Document():
    
    def __init__(self, title, raw_text):
        
        self.title = title
        self.raw_text = raw_text
        self.clean_text = ''
        self.tokens = set()
        self.num_tokens = 0

        self.preprocess_text()
        self.get_tokens()

    def preprocess_text(self):
        
        punctuation = "!\"#$%&()*+…-.,/:;<=>?@[\\]^_«»{|}~\n“”€—–"
        self.clean_text = self.raw_text.lower()
        self.clean_text = re.sub('[%s]' % re.escape(punctuation), '', self.clean_text)
        self.clean_text = re.sub('\w*\d\w*', '', self.clean_text)
        self.clean_text = re.sub("'", ' ', self.clean_text) # replaces ' with space
        self.clean_text = re.sub('\n', '', self.clean_text)
        self.clean_text = self.clean_text.split()
        # text = removeStopwords(text)

    def get_tokens(self):

        for i in self.clean_text:
            self.tokens.add(i)
            
        self.num_tokens = len(self.tokens)


class Query(Document):
    def __init__(self, query):
        super().__init__(title=None, raw_text=query)

c = Corpus()
c.add_document('one', text)
c.add_document('two', text2)