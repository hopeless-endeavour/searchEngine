import requests 
from bs4 import BeautifulSoup as bs
from bs4.dammit import EncodingDetector
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time 


def get_links(url):
    '''Returns transcript data from kwiziq '''

    resp = requests.get(url)
    http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = bs(resp.content, 'lxml', from_encoding=encoding)
    links = {}
    cefr  = ''
    id = 0
    for li in soup.find(class_='list-style').find_all('li'):
        temp = {}
        if li.find('h2') is not None:
            cefr = li.find('h2').get('id') 
        else:
            link = li.find('a').get('href')
            links[id] = {'link': link, 'cefr': cefr}
            id += 1

    return links
    
def get_texts(links):

    driver = webdriver.Chrome('C://Users/robda/Downloads/chromedriver_win32/chromedriver') 
    texts = {}

    id = 0
    for i in links.keys():
    
        print(i)
        driver.get('https://french.kwiziq.com'+ links[i]['link'])
        time.sleep(3)
        html = driver.page_source 
        soup = bs(html, 'lxml')
        name = links[i]['link'].replace('/learn/reading/', '')
        text = ''
        try:
            for p in soup.find(class_='reader').find_all('p'):
                text += ' ' + p.text

            texts[id] = {'name': name, 'cefr': links[i]['cefr'], 'text': text}
            id += 1
        except:
            print('error at: ', links[i]['link'])

    driver.close()   
    
    return texts

response = get_links('https://french.kwiziq.com/learn/reading#A1')
results = get_texts(response)

with open('cefr_texts.json', 'w') as f:
    json.dump(results, f)

