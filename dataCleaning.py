# Exploratory Data Analysis
from contextlib import closing

import pandas as pd
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
import pickle
import re
import string

def url_to_transcript(url):
    '''Returns transcript data specifically from thefrenchexperiment.com.'''
    # page = requests.get(url).text
    # soup = BeautifulSoup(page, "lxml")
    # text = [p.text for p in soup.find(class_="x-storycontent").find_all('p', class_="lan1")]
    # print(url)

    resp = requests.get(url)
    http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = BeautifulSoup(resp.content, 'lxml', from_encoding=encoding)
    text = [p.text for p in soup.find(class_="x-storycontent").find_all('p', class_="lan1")]
    print(url)
    return text

urls = ['https://www.thefrenchexperiment.com/stories/chicken-little',
        'https://www.thefrenchexperiment.com/stories/bird-and-whale',
        'https://www.thefrenchexperiment.com/stories/threepigs',
        'https://www.thefrenchexperiment.com/stories/goldilocks',
        'https://www.thefrenchexperiment.com/stories/petitchaperonrouge',
        'https://www.thefrenchexperiment.com/stories/uglyduckling']

names = ['chick-little', 'bird-and-whale', 'threepigs', 'goldilocks',
        'petitchaperonrouge', 'uglyduckling']

transcripts = [url_to_transcript(u) for u in urls]

for i, c in enumerate(names):
    with open("transcripts/" + c + ".txt", "wb") as file:
        pickle.dump(transcripts[i], file)

data = {}
for i, c in enumerate(names):
    with open("transcripts/" + c + ".txt", "rb") as file:
        data[c] = pickle.load(file)

def combine_text(list_of_text):
    '''Takes a list of text and combines them into one large chunk of text.'''
    combined_text = ' '.join(list_of_text)
    return combined_text

data_combined = {key: [combine_text(value)] for (key, value) in data.items()}

pd.set_option('max_colwidth', 150)
data_df = pd.DataFrame.from_dict(data_combined).transpose()
data_df.columns = ['transcript']
data_df = data_df.sort_index()
data_df.to_pickle("corpus.pkl")

def clean_text_round1(text):
    '''Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.'''
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text

round1 = lambda x: clean_text_round1(x)

data_clean = pd.DataFrame(data_df.transcript.apply(round1))
# print(data_clean)

def clean_text_round2(text):
    '''Get rid of some additional punctuation and non-sensical text that was missed the first time around.'''
    text = re.sub('[‘’“”«»…]', '', text)
    text = re.sub('\n', '', text)
    return text

round2 = lambda x: clean_text_round2(x)

data_clean = pd.DataFrame(data_clean.transcript.apply(round2))
# print(data_clean)

from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer()
data_cv = cv.fit_transform(data_clean.transcript)
data_dtm = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
data_dtm.index = data_clean.index
print(data_dtm)


data_dtm.to_pickle("dtm.pkl")
data_clean.to_pickle('data_clean.pkl')
pickle.dump(cv, open("cv.pkl", "wb"))
