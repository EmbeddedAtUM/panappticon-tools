import Event
import networkx as nx
from IO import *
from Global import Global
import sys
import string

# Routine to print all the nodes in a graph sorted by time
def DebugString(graph):
  lst = []
  for n in graph:
    event = graph.node[n]['data']
    event.thread_name = Global.ThreadName(event.pid, thread_name = event.thread_name)
    event.node_id = str(n)
    lst.append(event)
  lst.sort(key = lambda x: x.timestamp)
  return '\n'.join([str(e) for e in lst])

def ToGraphvizDotString(graph):
  return nx.to_agraph(graph).to_string()

# Routine for printing graph from file
def DebugPrintGraphFile(filename):
  g = LoadGraph(filename)
  return DebugString(g)

def PrintGraphFileToDot(filename):
  g = LoadGraph(filename)
  s = ToGraphvizDotString(g)
  for n in g:
    lst = string.split(n, '-')
    s = s.replace('-%s-' % lst[1], '-%s-' % Global.ThreadName(int(lst[1])))
  return s

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print('Usage: python DebugUtil.py <graph pickle file> <mode (0 or 1)> [thread name map file]')
    sys.exit(0)
  elif len(sys.argv) >= 4:
    Global.LoadThreadNameMap(sys.argv[3])

  if sys.argv[2] == '0':
    print(PrintGraphFileToDot(sys.argv[1]))
  elif sys.argv[2] == '1':
    print(DebugPrintGraphFile(sys.argv[1]))