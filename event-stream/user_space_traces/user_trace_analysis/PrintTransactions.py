import glob
from DebugUtil import *
from Global import Global
from ResourceCounting import *

def TransToString(graph):
  lst = []
  for n in graph:
    event = graph.node[n]['data']
    if event.event == 'UI_INPUT' or event.event == 'UI_UPDATE':
      event = graph.node[n]['data']
      event.thread_name = Global.ThreadName(event.pid)
      event.node_id = str(n)
      lst.append(event)
  lst.sort(key = lambda x: x.timestamp)
  input_time = lst[0].timestamp
  if len(lst) > 0:
    return '\n'.join([str(e) for e in lst]) + '\nTransaction time:' + str(lst[-1].timestamp - input_time)
  else:
    return ''
      
# Routine to print UI_INPUT and UI_UPDATE transactions for the user path
def PrintTrans(user_dir):
  Global.LoadThreadNameMap(user_dir + 'thread_name_map')
  for trans_file in glob.glob(user_dir + 'transactions/UI_INPUT*'):
    print('-------' + trans_file + '---------')
    g = LoadGraph(trans_file)
    print(TransToString(g))   
      

def PrintCriticalPaths(user_dir):
  Global.LoadThreadNameMap(user_dir + 'thread_name_map')
  for trans_file in glob.glob(user_dir + 'transactions/UI_INPUT*'):
    g = LoadGraph(trans_file)
    paths = CriticalPaths(g)
    for input_n in paths.keys():
      print('---------' + trans_file + '_' + input_n + '-------------')
      for update_path in paths[input_n]:
        path = update_path['path']
        print(PathToString(path) +'\nTransaction time:' + str(path[-1].timestamp - path[0].timestamp))


if __name__== '__main__':
  if len(sys.argv) < 2:
    print('Usage: python PrintTransaction.py <path to all transactions>')
    sys.exit(0)
  else:
    #PrintTrans(sys.argv[1])
    PrintCriticalPaths(sys.argv[1])
      
