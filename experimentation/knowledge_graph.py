class Node:
    def __init__(self, id, label, **kwargs):
        self.id = id 
        self.label = label
        self.attributes = dict()

        for key, value in kwargs.items():
            self.attributes[key] = value

class Edge:
    def __init__(self, type, startNode, endNode, **kwargs):
        self.type = type
        self.startNode = startNode 
        self.endNode = endNode
        self.attributes = dict()
        for key, value in kwargs.items():
            self.attributes[key] = value

class Graph:
    def __init__(self, adj=None):
       self.nodes = []
       self.edges = []
    
    def node(self, node_id):
        """ Returns node object given a node id """ 

        for i in self.nodes:
            if node_id == i.id:
                node = i
        
        return node
    
    def getNodeIDs(self):
        """ Returns a list of all node ids """    

        node_ids = []
        for i in self.nodes:
            node_ids.append(i.id)
        
        return node_ids
    
    def getEdges(self):
        """ Returns a list of tuples where each tuple is (start node id, end node id) """

        edge_ids = []
        for i in self.edges:
            edge = (i.startNode.id, i.endNode.id)
            edge_ids.append(edge)
        
        return edge_ids

    def addNode(self, node_id, label, **kwargs):

        if node_id in self.getNodeIDs():
            print("Node already exists.")
        else:
            node = Node(node_id, label, **kwargs)
            self.nodes.append(node)

    def addEdge(self, type, startNode_id, endNode_id, **kwargs):
        
        if (startNode_id and endNode_id) in self.getNodeIDs():
            if (startNode_id, endNode_id) not in self.getEdges():
                edge = Edge(type, self.node(startNode_id), self.node(endNode_id), **kwargs)
                self.edges.append(edge)
            else:
                print("Relation between nodes already exists")
        else:
            print("A node doesn't exist")



def scrapeUrl(url):
    """ Takes url, scrapes website, returns dict {url: {"state": "white", "content": "article text", links: [url1, url2, url3] }} where links is a list of all other articles the url points to """ 
    return web[url]           

def bfs(corpus, seedUrl, depth):
    queue = []
    visited = []
    graphAdj = {}
    currentNode = None
    
    # add first url to queue so it's visited first
    queue.append(seedUrl)

    while depth > 0: 
        if len(queue) != 0:
            # move item at beginning of queue into currentNode 
            currentNode = queue.pop(0) 
            # scrape the currentNode url to get it's data and links 
            urlDict = scrapeUrl(currentNode)
            graphAdj[currentNode] = urlDict
            print(graphAdj)
            # add the currentNode data to the corpus class/graph
            corpus.addNode(len(corpus.nodes), "DOC", raw_text=urlDict['content'])
            # append the currentNode to visited list after data has been collected 
            visited.append(currentNode)
            depth -= 1
            print("visited ", visited)
            # get all neighbouring links and add to queue 
            for i in graphAdj[currentNode]["links"]:
                if (i not in graphAdj) and (i not in queue):
                    queue.append(i)
            
            print('queue ' , queue)
        else:
            print("queue empty")
            break
        
    return visited 

web = {
        'A': {"content": 'from a', "links": ['B','D','E']},
        'B': {"content": 'from b',"links": ['A','D','C']},
        'C': {"content": 'from c', "links": ['B','G']},
        'D': {"content": 'from d', "links": ['A','B','E', 'F']},
        'E': {"content": 'from e', "links": ['A', 'D']},
        'F': {"content": 'from f', "links": ['D']},
        'G': {"content": 'from g',  "links": ['C']},
            
        }

G = Graph()
visited = bfs(G, 'A', 8)

# change bfs function to be recursive instead of while loop??
