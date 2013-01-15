# Global parameters

import networkx as nx

import Config
import IO
import gc
import os
import string
import sys

# This class is thread-unsafe
class Global:
  graph = nx.DiGraph()
  event_counter = 0
  # A connector is a map from connector_key to source node ID in the graph.
  # It is used to connect events between threads.
  connectors = {}
  # a map from thread id to the graph id of the last event of the thread
  active_threads = {}
  # a map from thread id to thread name
  thread_name_map = {}
  # a map for thread id to thread group id
  thread_group_map = {}
  # a map from app pid to set of WebView related threads
  webview_threads = {}
  # a map from thread id to current thread running state
  thread_state_map = {}
  # true if the user is in the system UI
  is_user_in_system_ui = False
  # last foreground application thread group id
  last_foreground_app_id = -1
  # a map to keep track of num of cores and DVFS state
  DUO    = 1
  SINGLE = 0
  ON     = 1
  OFF    = 0
  config_map = {'core': DUO, 'dvfs': ON}

  @staticmethod
  def ResetAll():
    print('Reset all global states (pid %d).' % os.getpid())
    Global.graph.clear()
    Global.connectors.clear()
    Global.active_threads.clear()
    Global.thread_group_map.clear()
    Global.thread_name_map.clear()
    Global.thread_state_map.clear()
    Global.webview_threads.clear()
    Global.last_foreground_app_id = -1
    gc.collect()
    sys.stderr.flush()
    sys.stdout.flush()
  
  ##########################################
  @staticmethod
  def NotifyUserInSystemUI(in_system_ui):
    Global.is_user_in_system_ui = in_system_ui
  
  @staticmethod
  def IsUserInSystemUI():
    return Global.is_user_in_system_ui
  ##################### Graph related #####################
  @staticmethod
  def PrintMemoryUsage():
    print('--------- process %d ----------' % os.getpid())
    print('connectors:%d' % sys.getsizeof(Global.connectors))
    print('active_threads:%d' % sys.getsizeof(Global.active_threads))
    print('thread_state_map:%d' % sys.getsizeof(Global.thread_state_map))
    print('webview_threads:%d' % sys.getsizeof(Global.webview_threads))
    print('number of nodes in graph:%d' % Global.graph.number_of_nodes())
    print('number of edges in graph:%d' % Global.graph.number_of_edges())

  @staticmethod
  def TryCleanupGraph(timestamp):
    Global.SaveThreadNameMap()
    Global.SaveWebViewThreadMap()
    subgraphs = nx.weakly_connected_component_subgraphs(Global.graph)
    for sg in subgraphs:
      any_event = sg.node[sg.nodes()[0]]['data']
      last_event_timestamp = any_event.timestamp
      start_event_timestamp = any_event.timestamp
      input_node = None
      for n in sg:
        if 'data' in Global.graph.node[n]:
          event = Global.graph.node[n]['data']
          last_event_timestamp = event.timestamp if event.timestamp > last_event_timestamp else last_event_timestamp
          start_event_timestamp = event.timestamp if event.timestamp < start_event_timestamp else start_event_timestamp
          if string.find(str(n), 'UI_INPUT') >= 0:
            input_node = str(n)
      # Remove graphs that are at least 10 seconds old or have span > 30 seconds
      if (timestamp - last_event_timestamp).total_seconds() > 30.0 or (last_event_timestamp - start_event_timestamp).total_seconds() > 300.0:
        IO.WriteGraph(sg, Config.transaction_graphs_dir, input_node)
        Global.graph.remove_nodes_from(sg.nodes())

  @staticmethod
  def Reset():
    print('Reset all graph states (pid %d).' % os.getpid())
    Global.graph.clear()
    Global.connectors.clear()
    Global.active_threads.clear()
    gc.collect()
    sys.stderr.flush()
    sys.stdout.flush()

  @staticmethod
  def Graph():
    return Global.graph

  @staticmethod
  def AddNode(node, key = None):
    node.core = Global.config_map['core']
    node.dvfs = Global.config_map['dvfs']
    if key:
      Global.graph.add_node(key, data=node)
    else:
      key = '%s-%d-%d' % (node.event, node.pid, Global.NextCounter())
      Global.graph.add_node(key, data=node)
    return key

  @staticmethod
  def AddEdge(src, dst):
    if src in Global.graph and 'data' in Global.graph.node[src]:
      Global.graph.add_edge(src, dst)

  @staticmethod
  def Connectors():
    return Global.connectors

  @staticmethod
  def ActiveThreads():
    return Global.active_threads
    
  @staticmethod
  def NextCounter():
    Global.event_counter += 1
    return Global.event_counter

  @staticmethod
  def ScheduleWriteGraph(synchronous = True):
    subgraphs = nx.weakly_connected_component_subgraphs(Global.graph)
    for sg in subgraphs:
      IO.WriteGraph(sg, Config.transaction_graphs_dir)
    Global.Reset()

  @staticmethod
  def NotifyThreadEnterForeground(tid):
    """Return true if a different application has entered foreground."""
    app_changed = True if Global.last_foreground_app_id != tid else False
    Global.last_foreground_app_id = tid
    return app_changed

  ##################### Thread name map related #####################
  @staticmethod
  def ThreadNameMap():
    return Global.thread_name_map

  @staticmethod
  def ThreadName(tid, thread_name = None):
    if thread_name is None:
      return '%s(%d)' % (Global.thread_name_map[tid][-1], tid) if tid in Global.thread_name_map else str(tid)
    else:
      return '%s(%d)' % (thread_name, tid)

  @staticmethod
  def AddThreadName(tid, name):
    if tid not in Global.thread_name_map:
      Global.thread_name_map[tid] = []
    Global.thread_name_map[tid].append(name)

    if (name == 'WebViewCoreThre') and (tid in Global.thread_group_map):
        tgid = Global.thread_group_map[tid]
        if tgid in Global.webview_threads:
          Global.webview_threads[tgid].add(tid)
        else:
          Global.webview_threads[tgid] = set([tid])

  @staticmethod
  def SaveThreadNameMap():
    IO.WriteString(str(Global.thread_name_map), Config.thread_name_map_file_location)

  @staticmethod
  def LoadThreadNameMap(filename = None):
    s = IO.ReadString(Config.thread_name_map_file_location if filename is None else filename)
    Global.thread_name_map = eval(s)

  ##################### Thread state related #####################
  @staticmethod
  def UpdateThreadState(event):
    tid = event.pid
    if event.event == 'CONTEXT_SWITCH':
      Global.thread_state_map[tid] = event.data['state']
    else:
      Global.thread_state_map[tid] = 'R'
  
  @staticmethod
  def ThreadState(tid):
    return 'D' if tid not in Global.thread_state_map else Global.thread_state_map[tid]

  ##################### Fork related #####################
  @staticmethod
  def NotifyFork(child_tid, parent_tid, tgid):
    Global.thread_group_map[child_tid] = tgid

  ##################### WebView threads map related #####################
  @staticmethod
  def NotifyForkWebView(child_tid, parent_tid, tgid):
    if tgid in Global.webview_threads:
      thread_set = Global.webview_threads[tgid]
      if parent_tid in thread_set:
        thread_set.add(child_tid)
  
  @staticmethod
  def isWebViewThread(tid):
    if tid not in Global.thread_group_map:
      return False
    tgid = Global.thread_group_map[tid]
    if tgid in Global.webview_threads:
      if tid in Global.webview_threads[tgid]:
        return True
    return False

  @staticmethod
  def SaveWebViewThreadMap():
    IO.WriteString(str(Global.webview_threads), Config.webview_thread_map_file_location)

  @staticmethod
  def LoadWebViewThreadMap(filename = None):
    s = IO.ReadString(Config.webview_thread_map_file_location if filename is None else filename)
    Global.webview_threads = eval(s)
  
  ##################### Config map related  #####################
  @staticmethod
  def NotifyCoreConfigChange(old_config, new_config):
    Global.config_map['core'] = new_config

  @staticmethod
  def NotifyDvfsConfigChange(old_config, new_config):
    Global.config_map['dvfs'] = new_config
