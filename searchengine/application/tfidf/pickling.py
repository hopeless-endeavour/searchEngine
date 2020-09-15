import pickle 
import pandas as pd 

def readData(path):

    corpus = []

    for i in os.listdir(path=path):
        with open(f'{path}/{i}','r', encoding="utf8") as f:
            full_data = f.read()
            json_obj = json.loads(full_data)

            if json_obj['text'] != " ":
                corpus.append([json_obj['title'], json_obj['text'], json_obj['url']])

    return corpus