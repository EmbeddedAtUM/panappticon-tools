import networkx as nx
import string

# Routine for pickling/unpickling a graph
def WriteGraph(sg, dir, input_node = None):
  if input_node:
    filename = dir + '/' + str(input_node) + '.gpickle'
    nx.write_gpickle(sg, filename)
  else:
    for node, degree in sg.in_degree_iter():
      if degree == 0 and string.find(str(node), 'UI_INPUT') >= 0:
        filename = dir + '/' + str(node) + '.gpickle'
        nx.write_gpickle(sg, filename)
        break

def LoadGraph(filename):
  return nx.read_gpickle(filename)

def WriteString(s, filename):
  f = open(filename, 'w+')
  f.write(s)
  f.close()

def ReadString(filename):
  f = open(filename)
  s = f.read()
  f.close()
  return s