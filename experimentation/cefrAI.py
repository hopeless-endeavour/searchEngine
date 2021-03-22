import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import json
import csv
import numpy as np
# import matplotlib.pyplot as plt
# from nn import LogisticRegression
# from searchengine.application.python_scripts.tf_idf import Corpus

with open('experimentation\cefr_texts.json') as f:
    data = json.load(f)

with open("experimentation\stop_words.txt", "r", encoding="utf-8") as f:
    stop_words = f.read().split("\n")[:-1]

x = [ data[str(i)]['text'] for i in range(len(data)) ]
y = [ data[str(i)]['cefr'] for i in range(len(data)) ]

x_train, x_test, y_train, y_test = train_test_split(x, y)

tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, encoding="utf-8", ngram_range=(1,2), stop_words=stop_words, max_features=1500)
features = tfidf.fit_transform(x_train).toarray()
labels = y_train

count_vect = CountVectorizer()
x_train_counts = count_vect.fit_transform(x_train)
tfidf_transformer = TfidfTransformer()
x_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(x_train_tfidf, y_train)


# vect.fit(x_train)
# x_train_vect = vect.fit_transform(x_train).toarray()

# cls = MultinomialNB()
# cls.fit(vect.transform(x_train), y_train)

# y_pred = cls.predict(vect.transform(x_test))
# print(accuracy_score(y_test, y_pred))
# print(classification_report(y_test, y_pred))

