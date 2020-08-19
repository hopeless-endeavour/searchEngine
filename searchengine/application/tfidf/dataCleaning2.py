import os
import re
import json

data = {'url': [],
        'title': [],
        'text': []}

# read in all json files
# combine all data into single dict
for i in os.listdir(path='data'):
    with open(f'data/{i}','r', encoding="utf8") as f:
        full_data = f.read()
        json_obj = json.loads(full_data)

        if json_obj['text'] != " ":
            data['url'].append(json_obj['url'])
            data['title'].append(json_obj['title'])
            data['text'].append(json_obj['text'])

def removeStopwords(text):
    with open("stop_words.txt", "r", encoding="utf-8") as f:
        stop_words = f.read().split("\n")[:-1]

    new_text = []
    for i in text:
        if i not in stop_words:
            new_text.append(i)

    return new_text

def preProcess(text):
    """ Tokenizes text, makes lowercase, removes punctuation, non-sensical
    text, digits and stop words. """

    punctuation = "!\"#$%&()*+-.,/:;<=>?@[\\]^_{|}~\n"
    stop_words = ""
    text = text.lower()
    text = re.sub('[%s]' % re.escape(punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text =  re.sub("'", ' ', text) # replaces ' with space
    text = re.sub('\n', '', text)
    text = text.split()
    text = removeStopwords(text)

    return text

def countVectorize(word_list):
    unique_words = set()
    vocab = {}

    for i in word_list:
        unique_words.add(i)

    for i, word in enumerate(sorted(unique_words)):
        vocab[i] = word

    return vocab

for i, text in enumerate(data['text']):
    data['text'][i] = preProcess(text)
