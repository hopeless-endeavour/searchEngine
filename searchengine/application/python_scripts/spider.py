from random import randint
from requests import get
from contextlib import closing
import re
from requests.exceptions import RequestException
from bs4 import BeautifulSoup as bs
import datetime
import random


class Spider:

    def __init__(self, seed):
        self.seed = seed 
        self.adj_graph = {}
        

    def _check_response(self, resp):
        """Returns true if response from url is html."""

        content_type = resp.headers["Content-Type"].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find("html") > -1)


    def _get_content(self, url):
        """Requests content of url. If invalid reponse, returns None."""

        try:
            with closing(get(url, stream=True)) as resp:
                if self._check_response(resp):
                    print("resp true")
                    return resp.content
                else:
                    return None

        except RequestException as e:
            print(f"Error during requests to {url} : {e}")
            return None

    def _crawl(self, url):
        print(f"crawling {url}")

        return {"title": "title", "content": "text", "author": "author", "published": "date_pub", "links": [random.randint(0,15)  for i in range(4)]}
    
    def _get_initial_links(self):

        # content = self._get_content(self.seed)
        # soup = bs(content, "html.parser")
        # urls = soup.find_all('a')
        # for i in urls:
        #     self.queue.append(self._check_url(i.get('href')))

        return [random.randint(0,20) for i in range(15)]

    def _check_url(self, url):

        if "http" not in url:  # doesn't add invalid href's
            return f"{self.seed}{url}"
        else:
            return url
        

    def _bfs(self, queue, visited, depth):

        if not queue:
            print("Queue is empty.")
            return self.adj_graph
        
        if depth > 0:
            v = queue.pop(0)
            self.adj_graph[v] = self._crawl(v)
            visited.append(v)
            print(f"visited: {visited}, depth: {depth}")
            for u in self.adj_graph[v]["links"]:
                if u not in self.adj_graph and u not in queue:
                    queue.append(u)
            print(f"queue at depth {depth}: {queue}")
            self._bfs(queue, visited, depth-1)
        else:
            print("Depth is 0.")
            return self.adj_graph

    def run(self, depth):

        queue = self._get_initial_links()
        # print(f"inital queue: {queue}")
        self._bfs(queue, [], depth)
        return self.adj_graph


class TwentyMinSpider(Spider):

    def __init__(self):
        super().__init__(seed="https://www.20minutes.fr")
    
    def _get_initial_links(self):

        queue = []
        content = self._get_content(self.seed)
        soup = bs(content, "html.parser")
        articles = soup.find("div", {'id': "page-content"}).find_all('article')
        for i in articles:
            queue.append(self._check_url(i.find('a').get('href')))

        return queue

    def _crawl(self, url):
        
        print(f"Attempting to crawl {url}")

        # get html from page 
        content = self._get_content(url)
        soup = bs(content, "html.parser")

        # find date published 
        info = soup.find("div", class_="nodeheader-infos")
        date_pub = info.find("time").get('datetime')
        date_pub = datetime.datetime.strptime(date_pub, "%Y-%m-%dT%H:%M:%S%z")

        # find title
        title = soup.find("h1", class_="nodeheader-title").text

        # find author 
        author = info.find('address', class_="authorsign").find("span", class_="authorsign-label")
        if author is not None:
            author = author.text 
        elif info.find('address', class_="authorsign").find("span", class_="author-name") is not None:
            author = info.find('address', class_="authorsign").find("span", class_="author-name").text
        else:
            author = "Unknown"
        
        # scrape text from page
        text = ''
        for i in soup.find('div', class_='content').find_all('p'):
            text += "\n" + i.text

        # crawl page for links to other articles
        links = []
        try: 
            for i in soup.find("ul", class_="block-list").find_all('a'):
                links.append(i.get("href"))
        except Exception as e:
            print(e)

        url_dict = {"title": title, "content": text, "author": author, "published": date_pub, "links": links}

        return url_dict

    
class FigaroSpider(Spider):
    def __init__(self):
        super().__init__(seed="https://www.lefigaro.fr/")
    
    def _get_initial_links(self):

        queue = []
        content = self._get_content(self.seed)
        soup = bs(content, "html.parser")
        articles = soup.find("div", {'class': "fig-main-wrapper"}).find_all('article')
        for i in articles:
            queue.append(self._check_url(i.find('a').get('href')))
        
        return queue

    def _crawl(self, url):
        
        print(f"Attempting to crawl {url}")

        # get html from page 
        content = self._get_content(url)
        soup = bs(content, "html.parser")

        # find date published 
        try:
            info = soup.find("div", class_="fig-content-metas-info")
            date_pub = info.find("time").get('datetime')
            date_pub = datetime.datetime.strptime(date_pub, "%Y-%m-%dT%H:%M:%S%z")
        except Exception as e:
            print(e)
            date_pub = None

        # find title
        title = soup.find("title").text

        # find author 
        author = soup.find('a', class_=["fig-content-metas__author", "header-info__author-link"])
        if author is not None:
            author = author.text 
        else:
            author = "Unknown"
        
        # scrape text from page
        text = ''
        for i in soup.find('article', class_=['fig-main', 'node-article']).find_all(['p', 'h2']):
            text += i.text

        # _crawl page for links to other articles
        links = []
        urls = soup.find_all("a", class_="fig-body-link__link")
        for i in urls:
            links.append(self._check_url(i.get("href")))

        return {"title": title, "content": text, "author": author, "published": date_pub, "links": links}


class FranceInfoSpider(Spider):
    def __init__(self):
        super().__init__(seed="https://www.francetvinfo.fr/")
    
    def _get_initial_links(self):

        queue = []
        content = self._get_content(self.seed)
        soup = bs(content, "html.parser")
        articles = soup.find_all("article")
        for i in articles:
            for j in i.find_all("a", class_="title"):
                queue.append(self._check_url(j.get('href')))

        return queue

    def _crawl(self, url):
        
        print(f"Attempting to _crawl {url}")

        # get html from page 
        content = self._get_content(url)
        soup = bs(content, "html.parser")

        # find date published 
        date_pub = soup.find("time").get('datetime')
        print(date_pub)
        date_pub = datetime.datetime.strptime(date_pub, "%Y-%m-%dT%H:%M:%S%z")

        # find title
        if soup.find("span", class_="c-title__main"):
            title = soup.find("span", class_="c-title__main").text
        elif soup.find("article", {"class": re.compile("content*")}).find("h1"):
            title = soup.find("article", {"class": re.compile("content*")}).find("h1").text
        else:
            print("Unknown title")
        print(title)

        # find author 
        author = soup.find('div', class_="c-signature__names")
        if author:
            author = author.text 
        elif soup.find("span", class_="author"):
            author = soup.find("span", class_="author").text
        else:
            author = "Unknown"
        print(author)
        
        # scrape text from page
        text = ''
        for i in soup.find('article', class_=['page-content', re.compile("content*")]).find_all(['p', 'h2']):
            text += i.text

        # _crawl page for links to other articles
        links = []
        if soup.find("ul", class_="same-topic__items"):
            articles = soup.find("ul", class_="same-topic__items").find_all("article")
            for i in articles:
                links.append(i.find("a").get("href"))
        elif soup.find("aside", class_="a-lire-aussi"):
            urls = soup.find("aside", class_="a-lire-aussi").find_all("a")
            for i in urls:
                links.append(self._check_url(i.get("href")))
        print(links)

        return {"title": title, "content": text, "author": author, "published": date_pub, "links": links}