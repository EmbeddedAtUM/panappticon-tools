import glob
import sys
from Global import Global
from IO import *
from EventCountHandlers import *

# Routine to print critical path between input and update
def PathToString(path):
  return '\n'.join([str(e) for e in path])

# Routine to get the critical path
def GetPath(g, input, update):
  path = nx.has_path(g, input, update)
  if not path:
    return False
  lst = []
  path = nx.shortest_path(g, input, update)
  for n in path:
    event = g.node[n]['data']
    event.thread_name = Global.ThreadName(event.pid)
    event.node_id = str(n)
    lst.append(event)
  return lst

# Remove all the outgoing edge of update node 
# to prune animation
def remove_out_edge(n, g):
  edges = g.out_edges(n)
  for edge in edges:
    g.remove_edge(edge[0], edge[1])


# Routine to extract the critical paths between input and 
# and update in a graph
def CriticalPaths(g):
  paths = {}
  update_lst = []
  input_lst = []
  # 1st pass: get the input node and last update node
  for n in g:
    evt = g.node[n]['data']
    if evt.event == 'UI_UPDATE':
      update_lst.append(n)
      remove_out_edge(n, g)
    if evt.event == 'UI_INPUT':
      input_lst.append(n)
  update_lst.sort(key = lambda x: g.node[x]['data'].timestamp)
  input_lst.sort(key = lambda x: g.node[x]['data'].timestamp)
  # 2nd pass: get the paths between input and last update node
  for input_n in input_lst:
    for update_n in update_lst:
      path = GetPath(g, input_n, update_n)
      if path:
        if input_n not in paths:
          paths[input_n] = []
        paths[input_n].append({'update': update_n, 'path':path}) 
  return paths 


#def PathProfile(path, gProfile):
#  profile = str(path[-1].timestamp - path[0].timestamp) + '\t' 
#  return profile + '\t'.join([str(e)+":"+str(gProfile[e]) for e in gProfile])


def PathProfile(input_evt, update_evt, gProfile):
  transaction = (update_evt.timestamp - input_evt.timestamp).total_seconds()
  core_config = 'Duo' if input_evt.core == 1 else 'Single'
  dvfs_config = 'On' if input_evt.dvfs == 1 else 'Off'
  return '%20s [%s.%s] [%s.%s] %7s %5s %.6f %.6f %.6f %.6f %.6f \
                  %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %6f %6f %6f'\
                  %(input_evt.thread_name, input_evt.json['time']['sec'], 
                  input_evt.json['time']['usec'],
                  update_evt.json['time']['sec'], 
                  update_evt.json['time']['usec'],
                  core_config, dvfs_config,
                  transaction, gProfile['IO'], gProfile['Network'],
                  gProfile['Msg'], gProfile['Binder'], gProfile['Async'],
                  gProfile['Fork'], gProfile['Update'], gProfile['Lock'],
                  gProfile['Futex'], gProfile['Waitqueue'],
                  gProfile['Runnable_wakeup'], gProfile['Runnable_tick'],
                  gProfile['Runnable_unknown'], gProfile['Block_unknown'],
                  gProfile['Max_msg_delay'])
  ''' return '%20s [%s.%s] [%s.%s] %7s %5s %.6f %.6f %.6f %.6f %.6f \
                  %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %6f %6f %6f'\
                  %(input_evt.thread_name, input_evt.timestamp.strftime('%s'), 
                  input_evt.timestamp.strftime('%f'),
                  update_evt.timestamp.strftime('%s'), 
                  update_evt.timestamp.strftime('%f'),
                  core_config, dvfs_config,
                  transaction, gProfile['IO'], gProfile['Network'],
                  gProfile['Msg'], gProfile['Binder'], gProfile['Async'],
                  gProfile['Fork'], gProfile['Update'], gProfile['Lock'],
                  gProfile['Futex'], gProfile['Waitqueue'],
                  gProfile['Runnable_wakeup'], gProfile['Runnable_tick'],
                  gProfile['Runnable_unknown'], gProfile['Block_unknown'],
                  gProfile['Max_msg_delay'])
'''


def ClearProfile(gProfile):
  for stat in gProfile:
    gProfile[stat] = 0

def ClearState(gState):
  ClearProfile(gState['profile'])
  gState['state'] = 'Running'
  gState['event'] = None

def GetPathProfile(path, gState):
  # update gState['profile']
  for evt in path:
    CountHandlerMap[evt.event](evt, gState)

def PrintInputPaths(input_n, input_paths, trans_file, g, gState):
  print('----------' + trans_file + '_' + input_n + '----------')
  print('%20s %19s %19s %7s %5s %8s %8s %8s %8s %8s \
                  %8s %8s %8s %8s %8s %8s %8s %8s %8s %8s %8s'\
                  %('app','start', 'end','core', 'dvfs','total','IO','Network',
                          'Msg','Binder','Async', 'Fork',
                          'Update','Lock','Futex','Wait',
                          'Wakeup','Tick', 'unk-R', 'unk-B', 'mx_msg'))
  #print(g.node[input_n]['data'])
  for path_to_update in input_paths:
    update_n = path_to_update['update']
   # print(g.node[update_n]['data'])
    path = path_to_update['path']
    GetPathProfile(path, gState)    
    print(PathProfile(path[0], path[-1], gState['profile'])) 
    ClearState(gState)
  

##################################################################

gProfile = {'IO': 0, 
            'Network': 0, 
            'Msg': 0, 
            'Binder': 0, 
            'Async': 0,
            'Fork': 0,
            'Update': 0,
            'Lock': 0, 
            'Futex':0,
            'Waitqueue':0,
            'Runnable_wakeup': 0,
            'Runnable_tick': 0,
            'Runnable_unknown':0,
            'Block_unknown': 0,
            'Max_msg_delay': 0
            }
gState = {'state': 'Running', 'event': None, 'profile': gProfile}

def new_main(trans_dir):
  Global.LoadThreadNameMap(trans_dir + 'thread_name_map')
  for trans_file in glob.glob(trans_dir + 'transactions/*'):
    #print trans_file
    g = LoadGraph(trans_file)
    paths = CriticalPaths(g)
    for input_n in paths.keys():
      PrintInputPaths(input_n, paths[input_n], trans_file, g, gState)


def old_main(filename):
  global gState
  g = LoadGraph(filename)
  paths = CriticalPaths(g)
  for input_n in paths.keys():
    #PrintInputPaths(input_n, paths[input_n], filename, g, gState)   
    print('---------'+ input_n + '--------------')
    update_paths = paths[input_n]
    for path_to_update in update_paths:
      path = path_to_update['path']
      print(PathToString(path))
      for evt in path:
        CountHandlerMap[evt.event](evt, gState)     
      print(PathProfile(path[0], path[-1], gProfile))
      ClearProfile(gProfile)


if __name__=='__main__':
  if len(sys.argv) < 3:
    print('Usage: python ResourceCounting.py < mode: 1: single file; 2: all files in a folder> < path to transaction file or all files in a folder>')
    sys.exit(0)
  else:
    if int(sys.argv[1]) == 1:
      # print individual transaction
      if len(sys.argv) >= 4:
        Global.LoadThreadNameMap(sys.argv[3])
      old_main(sys.argv[2])
    else:
      new_main(sys.argv[2])
