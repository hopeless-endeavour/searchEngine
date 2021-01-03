from random import randint
from requests import get
from contextlib import closing
from requests.exceptions import RequestException
from bs4 import BeautifulSoup as bs


class Spider:

    # TODO: get first article page from "seed"

    def __init__(self, seed, depth):
        self.visited_urls = []
        self.queue = []
        self.current_node = None
        self.adj_graph = {}
        self.VALID_DOMAINS = ["www.20minutes.fr"]
        self.depth = depth

        if self.check_domain(seed):
            self.seed = seed
        else:
            self.seed = None

    def check_response(self, resp):
        """Returns true if response from url is html."""

        content_type = resp.headers["Content-Type"].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find("html") > -1)

    def check_domain(self, url):

        for i in self.VALID_DOMAINS:
            if i in url:
                return True

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

    def crawl_20mins(self):
        """ Crawls and scraps www.20minutes.fr.  Returns dict of scraped content, where links is a list of all other articles the url points to """

        # TODO: scrape date of publication too
        print(f"Attempting to crawl 20mins at depth {self.depth}")

        content = self.get_content(self.currentNode)
        soup = bs(content, "html.parser")
        title = soup.find("h1", class_="nodeheader-title").text
        print(title)
        text = ''

        for i in soup.find('div', class_='content').find_all('p'):
            text += i.text

        links = []
        for i in soup.find("ul", class_="block-list").find_all('a'):
            links.append(i.get("href"))

        urlDict = {"title": title, "content": text, "links": links}

        return urlDict

    def crawl(self):

        if self.VALID_DOMAINS[0] in self.seed:
            return self.crawl_20mins()
        else:
            print("error")

    def bfs(self):

        # TODO: make recursive instead?

        self.queue.append(self.seed)

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
                # print("queue empty")
                break

        print(self.adj_graph)
        return self.adj_graph

    def run(self):

        if self.seed is not None:
            return self.bfs()
        else:
            print("Invalid domain")
