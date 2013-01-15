import Event
from networkx import nx
import sys

#################################################################
async_task_key_func = lambda event: 'async:%d' % event.data['runnable']

def futex_notify_key_func(event):
  pid = event.pid if 'pid' not in event.data else event.data['pid']
  return 'futex:%d,thread:%d' % (event.data['lock'], pid)

def wait_queue_notify_key_func(event):
  pid = event.pid if 'pid' not in event.data else event.data['pid']
  return 'waitqueue:%d,thread:%d' % (event.data['lock'], pid)

binder_key_func = lambda event: 'binder:%d' % event.data['trans']

#################################################################
def AddConnector(event, connector_key_func, node_id, connectors):
  ctor_key = connector_key_func(event)
  connectors[ctor_key] = node_id
  

def FindConnectorAndUpdateGraph(event, connector_key_func, node_id, connectors, graph):
  # find the connector
  ctor_key = connector_key_func(event)
  if ctor_key in connectors:
    graph.add_edge(connectors[ctor_key], node_id)
    del connectors[ctor_key]

#################################################################
def WaitQueueNotifyRHandler(node_id, evt, connectors, graph):
  AddConnector(evt, wait_queue_notify_key_func, node_id, connectors)


def WaitQueueWakeRHandler(node_id, evt, connectors, graph):
  FindConnectorAndUpdateGraph(evt, wait_queue_notify_key_func, node_id, connectors, graph)


def FutexNotifyRHandler(node_id, evt, connectors, graph):
  AddConnector(evt, futex_notify_key_func, node_id, connectors)


def FutexWakeRHandler(node_id, evt, connectors, graph):
  FindConnectorAndUpdateGraph(evt, futex_notify_key_func, node_id, connectors, graph)


def BinderProduceRHandler(node_id, evt, connectors, graph):
  AddConnector(evt, binder_key_func, node_id, connectors)


def BinderConsumeRHandler(node_id, evt, connectors, graph):
  FindConnectorAndUpdateGraph(evt, binder_key_func, node_id, connectors, graph)


ReorderHandlerMap = {'WAITQUEUE_NOTIFY': WaitQueueNotifyRHandler,
                     'WAITQUEUE_WAKE': WaitQueueWakeRHandler,
                     'FUTEX_NOTIFY': FutexNotifyRHandler,
                     'FUTEX_WAKE': FutexWakeRHandler,
                     'BINDER_PRODUCE_ONEWAY': BinderProduceRHandler,
                     'BINDER_PRODUCE_TWOWAY': BinderProduceRHandler,
                     'BINDER_PRODUCE_REPLY': BinderProduceRHandler,
                     'BINDER_CONSUME': BinderConsumeRHandler,
                     }

#################################################################
def LinkOtherEvents(node_id, connectors, graph):
  evt = graph.node[node_id]['data']
  if evt.event in ReorderHandlerMap:
    ReorderHandlerMap[evt.event](node_id, evt, connectors, graph)


def LinkUserSpaceEvents(node_id, graph, first_userspace_event_per_thread, last_userspace_event_per_thread):
  evt = graph.node[node_id]['data']
  if evt.event == 'WAITQUEUE_WAIT' or evt.event == 'FUTEX_WAIT':
    if evt.pid in last_userspace_event_per_thread:
      graph.add_edge(last_userspace_event_per_thread[evt.pid], node_id)
      del last_userspace_event_per_thread[evt.pid]
      del first_userspace_event_per_thread[evt.pid]
  elif evt.event == 'WAITQUEUE_WAKE' or evt.event == 'FUTEX_WAKE':
    if evt.pid in first_userspace_event_per_thread:
      graph.add_edge(node_id, first_userspace_event_per_thread[evt.pid])
      del last_userspace_event_per_thread[evt.pid]
      del first_userspace_event_per_thread[evt.pid]


def ReorderEvents(event_lst):
  if len(event_lst) == 0:
    return []
  node_id = 0
  graph = nx.DiGraph()
  connectors = {}
  last_event_per_cpu = {}
  last_userspace_event_per_thread = {}
  first_userspace_event_per_thread = {}
  # 1st pass: link all events belongs to the same core and same thread
  for evt in event_lst:
    graph.add_node(node_id, data=evt)
    if evt.cpu != 9:
      # kernel events
      if evt.cpu in last_event_per_cpu:
        graph.add_edge(last_event_per_cpu[evt.cpu], node_id)
      last_event_per_cpu[evt.cpu] = node_id
    else:
      # user space events
      if evt.pid in last_userspace_event_per_thread:
        graph.add_edge(last_userspace_event_per_thread[evt.pid], node_id)
      last_userspace_event_per_thread[evt.pid] = node_id
      if evt.pid not in first_userspace_event_per_thread:
        first_userspace_event_per_thread[evt.pid] = node_id
    node_id += 1
  # if all events are in one core, there is no need to do reordering
  if len(last_event_per_cpu.keys()) < 2 and len(first_userspace_event_per_thread.keys()) == 0:
    return event_lst
  # 2nd pass: extract all connector events
  for n in graph:
    LinkOtherEvents(n, connectors, graph)
  # 3rd pass: find all the events which the connector links to
  for n in graph:
    LinkOtherEvents(n, connectors, graph)
  # Do topological sort
  try:
    sorted_lst = nx.topological_sort(graph)
  except:
    sys.stderr.write('\n-----Found a cycle when doing reordering of the following events.-----\n')
    sys.stderr.write('\n'.join([str(e) for e in event_lst]))
    return event_lst
  if sorted_lst is None:
    return event_lst
  for n in sorted_lst:
    LinkUserSpaceEvents(n, graph, first_userspace_event_per_thread, last_userspace_event_per_thread)
  sorted_lst = nx.topological_sort(graph)
  if sorted_lst is None:
    return event_lst
  new_lst = []
  for n in sorted_lst:
    new_lst.append(graph.node[n]['data'])
  return new_lst


if __name__ == '__main__':
  event_lst = []
  for line in sys.stdin:
    event_lst.append(Event.decode_event(line))
  reordered_lst = ReorderEvents(event_lst)
  print('\n'.join([str(e) for e in reordered_lst]))
