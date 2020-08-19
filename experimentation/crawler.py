import requests
from bs4 import BeautifulSoup as bs

class Spider():

    # connect to database server
    # create database client

    # results storage
    results = []


    def crawl(self, seed, url, depth):
        
        try:
            print(f'Crawling url: {url} at depth: {depth}')
            response = requests.get(url)
        except:
            print(f'Failed to perform HTTP GET request on {url}\n')
            return

        soup = bs(response.text, 'html.parser')

        try:
            title = soup.find('title').text
            des = ''

            # for tag in soup.findAll():
            #     if tag.name == 'p':
            #         des += tag.text.strip().replace('\n', '')

        except:
            print("Title not found")
            return

        result = {
            'url': url,
            'title': title,
        }

        print(result['url'])

        if depth == 0:
            return

        links = soup.find_all('a')

        for link in links:
            try:
                if seed in link['href']:
                    self.crawl(seed, link['href'], depth - 1)
            except KeyError:
                pass


spider = Spider()
seed = 'https://www.20minutes.fr/'
spider.crawl(seed, seed, 1)
