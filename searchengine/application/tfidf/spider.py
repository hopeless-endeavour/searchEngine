from random import randint
from requests import get
from contextlib import closing
from requests.exceptions import RequestException
from bs4 import BeautifulSoup as bs
import datetime


class Spider:

    # TODO: get first article page from "seed"

    def __init__(self, seed, depth):
        self.visited_urls = []
        self.queue = []
        self.current_node = None
        self.adj_graph = {}
        self.depth = depth
        self.seed = seed 

    def check_response(self, resp):
        """Returns true if response from url is html."""

        content_type = resp.headers["Content-Type"].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find("html") > -1)


    def get_content(self, url):
        """Requests content of url. If invalid reponse, returns None."""

        try:
            with closing(get(url, stream=True)) as resp:
                if self.check_response(resp):
                    print("resp true")
                    return resp.content
                else:
                    return None

        except RequestException as e:
            print("Error during requests to {0} : {1}".format(url, str(e)))
            return None

    def crawl(self):
        pass
    
    def get_initial_links(self):

        content = self.get_content(self.seed)
        soup = bs(content, "html.parser")
        urls = soup.find_all('a')
        for i in urls:
            self.queue.append(self.check_url(i.get('href')))

    def check_url(self, url):

        if "http" not in url:  # doesn't add invalid href's
            return f"{self.seed}{url}"
        else:
            return url
        

    def bfs(self):

        # TODO: make recursive instead?

        while self.depth > 0:
            if len(self.queue) != 0:
                # move item at beginning of queue into currentNode
                self.currentNode = self.queue.pop(0)
                # scrape the currentNode url to get it's data and links
                urlDict = self.crawl()
                self.adj_graph[self.currentNode] = urlDict
                # add the currentNode data to the corpus class/graph
                # append the currentNode to visited list after data has been collected
                self.visited_urls.append(self.currentNode)
                self.depth -= 1
                # print("visited ", self.visited_urls)
                # get all neighbouring links and add to queue
                for i in self.adj_graph[self.currentNode]["links"]:
                    if (i not in self.adj_graph) and (i not in self.queue):
                        self.queue.append(i)

                # print('queue ' , self.queue)
            else:
                print("queue empty")
                break

        return self.adj_graph

    def run(self):

        if self.seed is not None:
            self.get_initial_links()
            return self.bfs()
        else:
            print("Invalid domain")


class TwentyMinSpider(Spider):

    def __init__(self, depth):
        super().__init__(depth=depth, seed="https://www.20minutes.fr")
    
    def get_initial_links(self):

        content = self.get_content(self.seed)
        soup = bs(content, "html.parser")
        articles = soup.find("div", {'id': "page-content"}).find_all('article')
        for i in articles:
            self.queue.append(self.check_url(i.find('a').get('href')))

    def crawl(self):
        
        print(f"Attempting to crawl {self.currentNode} at depth {self.depth}")

        # get html from page 
        content = self.get_content(self.currentNode)
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
        for i in soup.find("ul", class_="block-list").find_all('a'):
            links.append(i.get("href"))

        urlDict = {"title": title, "content": text, "author": author, "published": date_pub, "links": links}

        return urlDict

    
class FigaroSpider(Spider):
    def __init__(self, depth):
        super().__init__(depth=depth, seed="https://www.lefigaro.fr/")
    
    def get_initial_links(self):

        content = self.get_content(self.seed)
        soup = bs(content, "html.parser")
        articles = soup.find("div", {'class': "fig-main-wrapper"}).find_all('article')
        for i in articles:
            self.queue.append(self.check_url(i.find('a').get('href')))

    def crawl(self):
        
        print(f"Attempting to crawl {self.currentNode} at depth {self.depth}")

        # get html from page 
        content = self.get_content(self.currentNode)
        soup = bs(content, "html.parser")

        # find date published 
        info = soup.find("div", class_="fig-content-metas-info")
        date_pub = info.find("time").get('datetime')
        date_pub = datetime.datetime.strptime(date_pub, "%Y-%m-%dT%H:%M:%S%z")

        # find title
        title = soup.find("h1", class_="fig-headline").text

        # find author 
        author = info.find('a', class_="fig-content-metas__author")
        if author is not None:
            author = author.text 
        else:
            author = "Unknown"
        
        # scrape text from page
        text = ''
        for i in soup.find('article', class_='fig-main').find_all(['p', 'h2']):
            text += i.text

        # crawl page for links to other articles
        links = []
        urls = soup.find_all("a", class_="fig-body-link__link")
        for i in urls:
            links.append(self.check_url(i.get("href")))

        urlDict = {"title": title, "content": text, "author": author, "published": date_pub, "links": links}

        return urlDict


class FranceInfoSpider(Spider):
    def __init__(self,depth):
        super().__init__(depth=depth, seed="https://www.francetvinfo.fr/")
    
    def get_initial_links(self):

        content = self.get_content(self.seed)
        soup = bs(content, "html.parser")
        articles = soup.find_all("article")
        for i in articles:
            for j in i.find_all("a", class_="title"):
                self.queue.append(self.check_url(j.get('href')))


    def crawl(self):
        
        print(f"Attempting to crawl {self.currentNode} at depth {self.depth}")

        # get html from page 
        content = self.get_content(self.currentNode)
        soup = bs(content, "html.parser")

        # find date published 
        date_pub = soup.find("time").get('datetime')
        print(date_pub)
        date_pub = datetime.datetime.strptime(date_pub, "%Y-%m-%dT%H:%M:%S%z")

        # find title
        if soup.find("span", class_="c-title__main"):
            title = soup.find("span", class_="c-title__main").text
        elif soup.find("article", class_="content-video").find("h1"):
            title = soup.find("article", class_="content-video").find("h1").text
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
        for i in soup.find('article', class_=['page-content', "content-video"]).find_all(['p', 'h2']):
            text += i.text

        # crawl page for links to other articles
        links = []
        if soup.find("ul", class_="same-topic__items"):
            articles = soup.find("ul", class_="same-topic__items").find_all("article")
            for i in articles:
                links.append(i.find("a").get("href"))
        elif soup.find("aside", class_="a-lire-aussi"):
            urls = soup.find("aside", class_="a-lire-aussi").find_all("a")
            for i in urls:
                links.append(self.check_url(i.get("href")))
        print(links)

        urlDict = {"title": title, "content": text, "author": author, "published": date_pub, "links": links}

        return urlDict