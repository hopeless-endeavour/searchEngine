# 3000 common french words scraper 

import requests 
import time
import json
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

url = "https://3000mostcommonwords.com/list-of-3000-most-common-french-words-in-english/"


def get_texts(url):

    driver = webdriver.Chrome('C://Users/robda/Downloads/chromedriver_win32(1)/chromedriver') 
    
    words = {} # {'word': 'A1'}
    driver.get(url)
    
    
    for i in range(15):
        html = driver.page_source
        soup = bs(html, 'lxml') 
        for row in soup.find(class_='row-hover').find_all('tr'):
            w = row.find(class_="column-5").text
            lev = row.find(class_="column-4").text
            if w in words:
                words[w.lower()] += f", {lev}"
            else:
                words[w.lower()] = lev


        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="paginate_button next"]'))).click()
        except Exception as e:
            print(f"Error at {i}: {e.msg}")
            break
    

    # driver.close()   
    
    return words

words = get_texts(url)

with open('common_words.json', 'w') as f:
    json.dump(words, f)

