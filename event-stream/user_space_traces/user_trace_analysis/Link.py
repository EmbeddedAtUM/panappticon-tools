#!/usr/bin/env python

import datetime as dt

try:
  import ujson as jon
except:
  import json


class Link:
  def __init__(self, src, dest):
    self.src = src
    self.dest = dest
    self.time = dest.timestamp - src.timestamp
    self.link = GetType(src.event, dest.event)


def GetType(src, dest):
  link_type = 'DEFAULT_LINK'
  if src == 'ENQUEUE_MSG' and dest == 'DEQUEUE_MSG':
    link_type = 'MSG_LINK'
  elif src == 'BINDER_PRODUCE_TWOWAY' and dest == 'BINDER_CONSUME':
    link_type = 'BINDER_LINK'
  elif src == 'BINDER_PRODUCE_ONEWAY' and dest == 'BINDER_CONSUME':
    link_type = 'BINDER_LINK'
  elif src == 'BINDER_PRODUCE_REPLY' and dest == 'BINDER_CONSUME':
    link_type = 'BINDER_LINK'
  elif src == 'SUBMIT_ASYNCTASK' and dest == 'CONSUME_ASYNCTASK':
    link_type = 'ASYNC_LINK'
  elif src == 'UI_INVALIDATE' and dest == 'UI_UPDATE':
    link_type = 'UPDATE_LINK'
  return link_type
