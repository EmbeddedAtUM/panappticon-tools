import Event
from Global import Global

import copy

# Common utilities
def MarkCurrentWorkingUnitEnded(thread_id):
  threads = Global.ActiveThreads()
  if thread_id in threads:
    del threads[thread_id]


def AddConnector(event, connector_key_func, key):
  if key is None:
    return
  ctors = Global.Connectors()
  ctor_key = connector_key_func(event)
  ctors[ctor_key] = key
  
def FindConnectorAndUpdate(event, connector_key_func):
  ctors = Global.Connectors()
  threads = Global.ActiveThreads()

  # find the connector
  ctor_key = connector_key_func(event)
  if ctor_key in ctors:
    # connects previous event to the current event
    key = Global.AddNode(event)
    Global.AddEdge(ctors[ctor_key], key)
    del ctors[ctor_key]
    # decouple the previous event with the current event in the same thread
    threads[event.pid] = key

# Default and Null handlers
def DefaultHandlerInternal(event):
  """Use temporal correlation to link events within a thread."""
  threads = Global.ActiveThreads()

  tid = event.pid
  #key = None
  key = Global.AddNode(event)
  if tid in threads:
    Global.AddEdge(threads[tid], key)
    threads[tid] = key
  return key


def DefaultHandler(event):
  DefaultHandlerInternal(event)


def NullHandler(event):
  pass

# Binder event handlers
binder_key_func = lambda event: 'binder:%d' % event.data['trans']

def BinderProduceHandlerInternal(event):
  key = DefaultHandlerInternal(event)
  # insert a connector
  AddConnector(event, binder_key_func, key)


def BinderOneWayProduceHandler(event):
  if Global.IsUserInSystemUI():
    return
  BinderProduceHandlerInternal(event)


def BinderTwoWayProduceHandler(event):
  if Global.IsUserInSystemUI():
    return
  BinderProduceHandlerInternal(event)

  MarkCurrentWorkingUnitEnded(event.pid)


def BinderReplyHandler(event):
  if Global.IsUserInSystemUI():
    return
  BinderProduceHandlerInternal(event)

  MarkCurrentWorkingUnitEnded(event.pid)


def BinderConsumeHandler(event):
  if Global.IsUserInSystemUI():
    return
  ctors = Global.Connectors()
  threads = Global.ActiveThreads()

  # find a connector
  ctor_key = binder_key_func(event)
  if ctor_key in ctors:
    key = Global.AddNode(event)
    Global.AddEdge(ctors[ctor_key], key)
    del ctors[ctor_key]
    threads[event.pid] = key
    

# Native poll event handlers
def PollNativeHandler(event):
  if Global.IsUserInSystemUI():
    return
  MarkCurrentWorkingUnitEnded(event.pid)


def PollDoneHandler(event):
  if Global.IsUserInSystemUI():
    return
  MarkCurrentWorkingUnitEnded(event.pid)

# Async task event handlers
async_task_key_func = lambda event: 'async:%d' % event.data['runnable']

def AsyncTaskSubmitHandler(event):
  if Global.IsUserInSystemUI():
    return
  key = DefaultHandlerInternal(event)
  # insert a connector
  AddConnector(event, async_task_key_func, key)


def AsyncTaskConsumeHandler(event):
  if Global.IsUserInSystemUI():
    return
  FindConnectorAndUpdate(event, async_task_key_func)

# Message queue event handlers
msg_key_func = lambda event: 'thread:%d,message:%d' % (event.data['queue_id'], event.data['message_id'])

def EnqueueMessageHandler(event):
  if Global.IsUserInSystemUI():
    return
  key = DefaultHandlerInternal(event)
  # insert a connector
  AddConnector(event, msg_key_func, key)


def DequeueMessageHandler(event):
  if Global.IsUserInSystemUI():
    return
  FindConnectorAndUpdate(event, msg_key_func)
  
# Fork event handler
def ForkHandler(event):
  """ Create a 'FORK_IN_CHILD' event in the new thread."""
  threads = Global.ActiveThreads()
  
  # Add a node in the parent thread
  key = DefaultHandlerInternal(event)

  # Add a node in the child thread
  if key is not None:
    new_event = copy.deepcopy(event)
    new_event.event = 'FORK_IN_CHILD'
    new_event.pid = event.data['pid']
    new_event.json['event'] = new_event.event
    new_event.json['pid'] = new_event.pid
    new_key = Global.AddNode(new_event)
    threads[new_event.pid] = new_key
    Global.AddEdge(key, new_key)
    
  Global.NotifyFork(event.data['pid'], event.pid, event.data['tgid'])
  Global.NotifyForkWebView(event.data['pid'], event.pid, event.data['tgid'])
  
# Core config change event handler
def CoreConfigChangeHandler(event):
  Global.NotifyCoreConfigChange(event.data['old'], event.data['new'])

# DVFS config change event handler
def DVFSConfigChangeHandler(event):
  Global.NotifyDvfsConfigChange(event.data['old'], event.data['new'])

# UI Related event handler
def UIInputHandler(event):
  if Global.IsUserInSystemUI():
    return
  threads = Global.ActiveThreads()
  event.thread_name = Global.ThreadName(event.pid)
  key = Global.AddNode(event)
  threads[event.pid] = key


ui_invalidate_key_func = lambda event: 'invalidate:%d' % event.pid
def UIInvalidateHandler(event):
  if Global.IsUserInSystemUI():
    return
  key = DefaultHandlerInternal(event)
  # insert a connector
  AddConnector(event, ui_invalidate_key_func, key)  


def UIUpdateHandler(event):
  if Global.IsUserInSystemUI():
    return
  FindConnectorAndUpdate(event, ui_invalidate_key_func)


def UIInvalidateV2Handler(event):
  if Global.IsUserInSystemUI():
    return
  key = DefaultHandlerInternal(event)
  # insert a connector
  if key is None:
    return
  ctors = Global.Connectors()
  ctor_key = ui_invalidate_key_func(event)
  if ctor_key in ctors:
    ctors[ctor_key].append(key)
  else:
    ctors[ctor_key] = [ key, ]


def UIUpdateV2Handler(event):
  if Global.IsUserInSystemUI():
    return
  ctors = Global.Connectors()
  threads = Global.ActiveThreads()

  event.thread_name = Global.ThreadName(event.pid)
  # find the connector
  ctor_key = ui_invalidate_key_func(event)
  if ctor_key in ctors:
    # connects all previous events to the current event
    key = Global.AddNode(event)
    for n in ctors[ctor_key]:
      Global.AddEdge(n, key)
    del ctors[ctor_key]
    # decouple the previous event with the current event in the same thread
    threads[event.pid] = key

# Enter/Exit foreground event handlers
def EnterForegroundHandler(event):
  Global.SaveThreadNameMap()
  Global.SaveWebViewThreadMap()
  if Global.NotifyThreadEnterForeground(event.pid):
    Global.ScheduleWriteGraph(synchronous = False)
  if Global.ThreadName(event.pid) == 'ndroid.launcher':
    Global.NotifyUserInSystemUI(True)
  else:
    Global.NotifyUserInSystemUI(False)

def ExitForegroundHandler(event):
  pass

# Thread name event handler
def ThreadNameHandler(event):
  # TODO: temporary hack to guess reboot event
  if event.data['pid'] == 7:
    Global.ScheduleWriteGraph(synchronous = False)
    Global.ResetAll()
  Global.AddThreadName(event.data['pid'], event.data['name'])
  
# Futex related handler specific for WebView applications
def FutexWaitHandler(event):
  if Global.IsUserInSystemUI():
    return
  if Global.isWebViewThread(event.pid):
    MarkCurrentWorkingUnitEnded(event.pid)
  else:
    DefaultHandler(event)


def futex_notify_key_func(event):
  pid = event.pid if 'pid' not in event.data else event.data['pid']
  return 'futex:%d,thread:%d' % (event.data['lock'], pid)


def FutexWakeHandler(event):
  if Global.IsUserInSystemUI():
    return
  if Global.isWebViewThread(event.pid):
    FindConnectorAndUpdate(event, futex_notify_key_func)
  else:
    DefaultHandler(event)

def FutexNotifyHandler(event):
  if Global.IsUserInSystemUI():
    return
  if Global.isWebViewThread(event.data['pid']):
    key = DefaultHandlerInternal(event)
    AddConnector(event, futex_notify_key_func, key)

# Waitqueue event related handler for WebView applications
def WaitQueueWaitHandler(event):
  if Global.IsUserInSystemUI():
    return
  if Global.isWebViewThread(event.pid):
    MarkCurrentWorkingUnitEnded(event.pid)
  else:
    DefaultHandler(event)

def wait_queue_notify_key_func(event):
  pid = event.pid if 'pid' not in event.data else event.data['pid']
  return 'waitqueue:%d,thread:%d' % (event.data['lock'], pid)


def WaitQueueWakeHandler(event):
  if Global.IsUserInSystemUI():
    return
  if Global.isWebViewThread(event.pid):
    FindConnectorAndUpdate(event, wait_queue_notify_key_func)
  else:
    DefaultHandler(event)

def WaitQueueNotifyHandler(event):
  if Global.IsUserInSystemUI():
    return
  if Global.isWebViewThread(event.data['pid']):
    key = DefaultHandlerInternal(event)
    AddConnector(event, wait_queue_notify_key_func, key)
    # insert a FAKED_WAITQUEUE_WAKE event in the notified thread
    thread_state = Global.ThreadState(event.data['pid'])
    if (key is not None) and (thread_state == 'I' or thread_state == 'U'):
      new_event = copy.deepcopy(event)
      new_event.event = 'FAKED_WAITQUEUE_WAKE'
      new_event.pid = event.data['pid']
      del new_event.data['pid']
      new_event.json['event'] = new_event.event
      new_event.json['pid'] = new_event.pid
      new_key = Global.AddNode(new_event)
      threads = Global.ActiveThreads()
      threads[new_event.pid] = new_key
      Global.AddEdge(key, new_key)

# Context switch event handler
def ContextSwitchHandler(event):
  if Global.IsUserInSystemUI():
    return
  if Global.isWebViewThread(event.data['old']) and Global.ThreadState(event.data['old']) != 'R':
    MarkCurrentWorkingUnitEnded(event.data['old'])
  else:
    DefaultHandler(event)
