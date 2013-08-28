from osm2networkx import *
import random
import math

"""
Searching a street network using Breadth First Search

REQUIREMENTS:

  networkx: http://networkx.github.io/

REFERENCES:

  [1] Russel, Norvig: "Artificial Intelligene A Modern Approach", 3rd ed, Prentice Hall, 2010

ASSIGNMENT:

  Extend this program to Tridirectional Search.
  Find a path between three starting points.

author: Daniel Kohlsdorf and Thad Starner
"""

"""
The state space in our problem hold:

   1) A node in the street graph
   2) A parent node

"""

# Haversine formula example in Python
# Author: Wayne Dyck
# Modified: Ruffin White

def distance(node, child):
    
    lat1, lon1 = [node.node['data'].lat, node.node['data'].lon]
    lat2, lon2 = [child.node['data'].lat, child.node['data'].lon]
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

#def distance(node, child):
#    
#    lat1, lon1 = [node.node['data'].lat, node.node['data'].lon]
#    lat2, lon2 = [child.node['data'].lat, child.node['data'].lon]
#    
#    d = math.sqrt( (lat2-lat1)*(lat2-lat1) + (lon2-lon1)*(lon2-lon1) )
#
#    return d


class State:

    def __init__(self, node, parent, cost = 0, seeds = None):
        self.node   = node
        self.parent = parent
        self.cost = cost
        self.seed = seeds

    def __eq__(self, other):
        if isinstance(other, State):
            return self.node['data'].id == other.node['data'].id
        return NotImplemented
        
    def __hash__(self):
        return hash(self.node['data'].id)
        
class Path:

    def __init__(self, start, stop, cost, joint = False):
        self.start  = start
        self.stop   = stop
        self.cost   = cost
        self.joint   = joint

    def __eq__(self, other):
        if isinstance(other, Path):
            if(self.joint):
                same = (self.start.seed == other.start.seed) and (self.stop.seed == other.stop.seed)
                swap = (self.start.seed == other.stop.seed) and (self.stop.seed == other.start.seed)
            else:
                same = (self.start == other.start) and (self.stop == other.stop)
                swap = (self.start == other.stop) and (self.stop == other.start)
            return same or swap
        return NotImplemented
        
    def __hash__(self):
        return hash(self.start.node['data'].id) ^ hash(self.stop.node['data'].id)
    
    def __str__(self):
            if(self.joint):
                return str(self.start.seed.node['data'].id + " -> " + self.stop.seed.node['data'].id)
            else:
                return str(self.start.node['data'].id + " -> " + self.stop.node['data'].id)
    
"""
Implements BFS on our GPS data

see [1] Figure 3.11
"""
def bfs(graph, start, goal):
    if start == goal:
        print "START === GOAL"
        return None
    
    frontier = [start]
    explored = []
    num_explored = 0
    while len(frontier) > 0:
       node = frontier.pop(0)
       explored.append(node)
       
       for edge in networkx.edges(graph, node.node['data'].id):
           child = State(graph.node[edge[1]], node, node.cost)
           if (child not in explored) and (child not in frontier):
                child.cost += distance(node, child)
                # HINT: Goal - Check
                if child == goal:
                    print "Goal found"
                    print "  Explored: ", num_explored
                    print "      Cost: ", child.cost, "\n\n"
                    return child
                else:
                    frontier.append(child)
                num_explored = num_explored + 1
    print "No path found, explored: ", num_explored

    return None

"""
Backtrack and output your solution
"""
def backtrack(state, graph):
    if state.parent != None:
        print "Node: ", state.node['data'].id
        if len(state.node['data'].tags) > 0:            
            for key in state.node['data'].tags.keys():
                print "       N: ", key, " ", state.node['data'].tags[key]        
              
        for edge in networkx.edges(graph, state.node['data'].id):
            if len(graph.node[edge[1]]['data'].tags) > 0:
                for key in graph.node[edge[1]]['data'].tags:
                    print "       E: ", graph.node[edge[1]]['data'].tags[key]
        backtrack(state.parent, graph)
