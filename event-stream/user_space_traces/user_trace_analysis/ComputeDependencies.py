#!/usr/bin/env python
import sys
import Event
from EventHandlerMap import event_handler_map
from Global import Global
from EventReordering import ReorderEvents

def ReorderAndHandleEvents(event_list):
  reordered_lst = ReorderEvents(event_list)
  for evt in reordered_lst:
    #print(str(evt))
    # Common handling
    Global.UpdateThreadState(evt)
    # Event-specific handling
    event_handler_map[evt.event](evt)
  del reordered_lst

def new_main():
  event_list = []
  current_time = None
  for line in sys.stdin:
    event = Event.decode_event(line)
    if current_time != event.timestamp:
      ReorderAndHandleEvents(event_list)
      del event_list
      event_list = []
    event_list.append(event)
    current_time = event.timestamp
    if Global.Graph().number_of_nodes() > 1000000:
      Global.PrintMemoryUsage()
      Global.TryCleanupGraph(event.timestamp)
      Global.PrintMemoryUsage()
      sys.stderr.flush()
      sys.stdout.flush()

  ReorderAndHandleEvents(event_list)
  del event_list

def old_main():
  for line in sys.stdin:
    event = Event.decode_event(line)
     # Common handling
    Global.UpdateThreadState(event)
    # Event-specific handling
    event_handler_map[event.event](event)

if __name__ == '__main__':
  new_main()

  Global.ScheduleWriteGraph()