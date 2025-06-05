import random 
import string 

class Graph:
    def __intit__(self):
        self.nodes = []
        self.edges = []

    
    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_vertices(self):
        return self.nodes
    
    def get_edges(self):
        return self.edges
    

class Node:
    def __init__(self,id,label,type):
        self.id = id
        self.label = label
        self.type = type

class Edge:
    def __init__(self, origin, destination, weight):
        self.origin = origin
        self.destination = destination
        self.weight = weight



