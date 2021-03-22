import datetime
import re
from random import randint
from requests import get
from requests.exceptions import RequestException
from contextlib import closing

from bs4 import BeautifulSoup as bs


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
    
    def _check_url(self, url):
        """ Validates url. Returns correct url. """

        if "http" not in url:  # doesn't add invalid href's
            return f"{self.seed}{url}"
        else:
            return url

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
        """ Crawls content of given url. """

        print(f"crawling {url}")

         # find title
        title = soup.find("title").text

        # scrape text from page
        text = ''
        for i in soup.find_all(['p','h1']):
            text += "\n" + i.text

        # _crawl page for links to other articles
        links = []
        urls = soup.find_all("a")
        for i in urls:
            links.append(self._check_url(i.get("href")))

        return {"title": title, "content": text, "links": links}
    
    def _get_initial_links(self):
        """ Gets initial links on seed domain, returns as initial queue. """

        queue = []
        content = self._get_content(self.seed)
        soup = bs(content, "html.parser")
        urls = soup.find_all('a')
        for i in urls:
            queue.append(self._check_url(i.get('href')))

        return queue      

    def _bfs(self, queue, visited, depth):
        """ Recursive breadth first search """

        if not queue:
            print("Queue is empty.")
            return 
        
        if depth > 0:
            # set current node to first item in queue, and remove from queue
            current_node = queue.pop(0)
            url_dict = self._crawl(current_node)
            print(f"current node: {current_node}, url_dict: {url_dict}, depth: {depth}")
            # if not url_dict, the node couldn't be crawled
            if url_dict:
                    # add crawled node to adj_graph
                    self.adj_graph[current_node] = url_dict
                    # add all the links from the current node into the queue
                    for u in self.adj_graph[current_node]["links"]:
                        # only add to queue if it hasn't already been crawled and isn't in the queue already
                        if u not in self.adj_graph and u not in queue:
                            queue.append(u)

            # add current node to visited list 
            visited.append(current_node)
            print(f"visited: {visited}")
            
            print(f"queue at depth {depth}: {queue}")
            # call self with a depth - 1 
            self._bfs(queue, visited, depth-1)
        else:
            print("Depth is 0.")
            return 

    def run(self, depth):

        # initialise queue 
        queue = self._get_initial_links()
        print(f"inital queue: {queue}")
        # call first occurance of bfs to start crawl with empty visited list []
        self._bfs(queue, [], depth)
        return self.adj_graph


class TwentyMinSpider(Spider):

    def __init__(self):
        super().__init__(seed="https://www.20minutes.fr")
    
    def _get_initial_links(self):

        queue = []
        content = self._get_content(self.seed)

        if content:
            soup = bs(content, "html.parser")
            articles = soup.find("div", {'id': "page-content"}).find_all('article')
            for i in articles:
                queue.append(self._check_url(i.find('a').get('href')))

            return queue

        else:
            return None

    def _crawl(self, url):
        
        print(f"Attempting to crawl {url}")

        # get html from page 
        content = self._get_content(url)

        if not content:
            return None 

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
        for i in soup.find('div', class_='content').find_all(['p','h1']):
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
        try:
            for i in soup.find('article', class_=['fig-main', 'node-article']).find_all(['p', 'h2']):
                text += "\n" + i.text
        except:
            return None

        # _crawl page for links to other articles
        links = []
        urls = soup.find_all("a", class_="fig-body-link__link")
        for i in urls:
            links.append(self._check_url(i.get("href")))

        url_dict = {"title": title, "content": text, "author": author, "published": date_pub, "links": links}

        return url_dict



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
            text += "\n" + i.text

        # crawl page for links to other articles
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

        url_dict = {"title": title, "content": text, "author": author, "published": date_pub, "links": links}

        return url_dict