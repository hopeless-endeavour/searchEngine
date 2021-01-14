import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import json
import csv
import numpy as np
import matplotlib.pyplot as plt

# with open('cefr_texts.json') as f:
#     data = json.load(f)

# data = data.values()

# csv_file = open('cefr_texts.csv', 'w', encoding='utf8') 

# csv_writer = csv.writer(csv_file)

# count = 0
# for i in data:
#     if count == 0:

#         header = i.keys()
#         csv_writer.writerow(header)
#         count +=1

#     csv_writer.writerow(i.values())

# csv_file.close()
# with open("./stop_words.txt", "r", encoding="utf-8") as f:
#     stop_words = f.read().split("\n")[:-1]

# data = pd.read_csv('cefr_texts.csv', sep=',', header=0)

# x = data.text
# y =  data.cefr

# x_train, x_text, x_train, y_train = train_test_split(x, y)

# vect = TfidfVectorizer(stop_words=stop_words, max_features=1500)
# # vect.fit(x_train)
# x_train_vect = vect.fit_transform(x_train).toarray()

# cls = MultinomialNB()
# cls.fit(vect.transform(x_train), y_train)

# y_pred = cls.predict(vect.transform(x_text))
# print(accuracy_score(y_test, y_pred))
# print(classification_report(y_test, y_pred))
