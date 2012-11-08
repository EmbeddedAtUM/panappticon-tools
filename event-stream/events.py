#!/usr/bin/env python

import datetime as dt
import string
import time

try:
    import ujson as json
except:
    import json

def format_timestamp(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")

def format_hertz(quantity, multiplier):
    hertz = float(quantity) * float(multiplier)
    if (hertz < 10**3):
        magnitude = hertz
        suffix = "Hz"
    elif (hertz < 10**6):
        magnitude = hertz / 10**3
        suffix = "KHz"
    elif (hertz < 10**9):
        magnitude = hertz / 10**6
        suffix = "MHz"
    else:
        magnitude = hertz / 10**9
        suffix = "GHz"
    return "%g %s"%(magnitude, suffix)

class Event(object):
    def __init__(self, data):
        self.timestamp = dt.datetime.fromtimestamp(data['time']['sec']).replace(microsecond=data['time']['usec'])
        self.cpu = data['cpu']
        self.pid = data['pid']
        self.irq = data['irq']
        self.event = data['event']
        self.data = data['data']

    def __str__(self):
        return "[%s] <%s> (%7s) %16s"%(format_timestamp(self.timestamp),
                                     self.cpu,
                                     "I %5s"%self.pid if self.irq else self.pid,
                                     self.event.replace('_',' ').capitalize())

class SyncLogEvent(Event):
    def __init__(self, data):
        super(SyncLogEvent, self).__init__(data)
        self.magic = self.data['magic']

    def __str__(self):
        header = super(SyncLogEvent, self).__str__()
        return "%s: '%s'"%(header, self.magic)

class MissedCountEvent(Event):
    def __init__(self, data):
        super(MissedCountEvent, self).__init__(data)
        self.count = self.data['count']

    def __str__(self):
        header = super(MissedCountEvent, self).__str__()
        return "%s: %d"%(header, self.count)

class HotCpuEvent(Event):
    def __init__(self, data):
        super(HotCpuEvent, self).__init__(data)
        self.hot_cpu = self.data['cpu']
    
    def __str__(self):
        header = super(HotCpuEvent, self).__str__()
        return "%s: %d"%(header, self.hot_cpu)

class BinderEvent(Event):
    def __init__(self, data):
        super(BinderEvent, self).__init__(data)
        self.transaction = self.data['trans']

    def __str__(self):
        header = super(BinderEvent, self).__str__()
        return "%s: %0x"%(header, self.transaction)

class  CpuFreqSetEvent(Event):
    def __init__(self, data):
        super(CpuFreqSetEvent, self).__init__(data)
        self.cpufreq_cpu = self.data['cpu']
        self.old_khz = self.data['old_khz']
        self.new_khz = self.data['new_khz']
    
    def __str__(self):
        header = super(CpuFreqSetEvent, self).__str__()
        return "%s: [%d] %s => %s"%(header, self.cpufreq_cpu, format_hertz(self.old_khz, 1000), format_hertz(self.new_khz, 1000))

class GeneralLockEvent(Event):
    def __init__(self, data):
        super(GeneralLockEvent, self).__init__(data)
        self.lock = self.data['lock']
    
    def __str__(self):
        header = super(GeneralLockEvent, self).__str__()
        return "%s:       [%0x]"%(header, self.lock)

class GeneralNotifyEvent(Event):
    def __init__(self, data):
        super(GeneralNotifyEvent, self).__init__(data)
        self.lock = self.data['lock']
        self.notify_pid = self.data['pid']
    
    def __str__(self):
        header = super(GeneralNotifyEvent, self).__str__()
        return "%s: %5d [%0x]"%(header, self.notify_pid, self.lock)

class WakeLockEvent(Event):
    def __init__(self, data):
        super(WakeLockEvent, self).__init__(data)
        self.lock = self.data['lock']
        self.timeout = self.data['timeout']

    def __str__(self):
        header = super(WakeLockEvent, self).__str__()
        return "%s: [%0x] %s"%(header, self.lock, "timeout: %d"%(self.timeout) if self.timeout else "")

class WakeUnlockEvent(Event):
    def __init__(self, data):
        super(WakeUnlockEvent, self).__init__(data)
        self.lock = self.data['lock']
        
    def __str__(self):
        header = super(WakeUnlockEvent, self).__str__()
        return "%s: [%0x]"%(header, self.lock)

class ForkEvent(Event):
    def __init__(self, data):
        super(ForkEvent, self).__init__(data)
        self.fork_pid = self.data['pid']
        self.fork_tgid = self.data['tgid']
        
    def __str__(self):
        header = super(ForkEvent, self).__str__()
        return "%s: pid: %5d tgid: %5d"%(header, self.fork_pid, self.fork_tgid)

class ThreadNameEvent(Event):
    def __init__(self, data):
        super(ThreadNameEvent, self).__init__(data)
        self.thread_pid = self.data['pid']
        self.thread_name = self.data['name']
        
    def __str__(self):
        header = super(ThreadNameEvent, self).__str__()
        return "%s: %5d=>'%s'"%(header, self.thread_pid, self.thread_name)

class ContextSwitchEvent(Event):
    state_map = {'R' : "Running",
                 'I' : "Interruptible",
                 'U' : "Uninterruptible",
                 'S' : "Stopped",
                 'T' : "Traced",
                 'D' : "Dead",
                 'W' : "Wakekill"}

    def __init__(self, data):
        super(ContextSwitchEvent, self).__init__(data)
        self.old_pid = self.data['old']
        self.new_pid = self.data['new']
        self.state   = self.data['state']

    def __str__(self):
        header = super(ContextSwitchEvent, self).__str__()
        return "%s: %5d => %5d (%s)"%(header, self.old_pid, self.new_pid, self.state_map[self.state])

# Userspace Events
class Event(object):
    def __init__(self, data):
        self.timestamp = dt.datetime.fromtimestamp(data['time']['sec']).replace(microsecond=data['time']['usec'])
        self.cpu = data['cpu'] #no
        self.pid = data['pid'] #yes
        self.irq = data['irq'] #no
        self.event = data['event']
        self.data = data['data']

    def __str__(self):
        return "[%s] <%s> (%7s) %16s"%(format_timestamp(self.timestamp),
                                     self.cpu,
                                     "I %5s"%self.pid if self.irq else self.pid,
                                     self.event.replace('_',' ').capitalize())

class UserspaceEvent(Event):
    def __init__(self, data):
        data['cpu'] = -1
        data['irq'] = False
        super(UserspaceEvent, self).__init__(data)

class MessageQueueEvent(UserspaceEvent):
    def __init__(self, data):
        super(MessageEnqueueEvent, self).__init__(data)
        self.message_id = self.data['mid']
        self.queue_id = self.data['qid']
        
    def __str__(self):
        header = super(MessageQueueEvent, self).__str__()
        return "%s: Queue: %3d Message: %3d"%(header, self.message_id, self.queue_id)

    
class MessageQueueDelayEvent(UserspaceEvent):
    def __init__(self, data):
        super(MessageEnqueueDelayEvent, self).__init__(data)
        self.delay = self.data['delay']
        
    def __str__(self):
        header = super(MessageQueueDelayEvent, self).__str__()
        return "%s: %d"%(header, self.delay)

class ExecutorEvent(UserspaceEvent):
    def __init__(self, data):
        super(ExecutorEvent, self).__init__(data)
        self.runnable = self.data['runnable']
        
    def __str__(self):
        header = super(ExecutorEvent, self).__str__()
        return "%s: %0x"%(header, self.runnable)

class SwitchConfigEvent(UserspaceEvent):
    def __init__(self, data):
        super(SwitchConfigEvent, self).__init__(data)
        self.core = self.data['core']
        self.dvfs = self.data['DVFS']
        
    def __str__(self):
        header = super(SwitchConfigEvent, self).__str__()
        return "%s: Core: %s DVFS: %s"%(header, self.core, self.dvfs)

class UserspaceTagEvent(UserspaceEvent):
    def __init__(self, data):
        super(UserspaceTagEvent, self).__init__(data)
    
    def __str__(self):
        header = super(UserspaceTagEvent, self).__str__()
        return "%s"%(header)

def decode_event(encoded):
    data = json.loads(encoded)
    return {
        "SYNC_LOG" : SyncLogEvent,
        "MISSED_COUNT" : MissedCountEvent,
        "CPU_ONLINE" : HotCpuEvent,
        "CPU_DOWN_PREPARE" : HotCpuEvent,
        "CPU_DEAD" : HotCpuEvent,
        "CPUFREQ_SET" : CpuFreqSetEvent,
        "BINDER_PRODUCE_ONEWAY" : BinderEvent,
        "BINDER_PRODUCE_TWOWAY" : BinderEvent,
        "BINDER_PRODUCE_REPLY" : BinderEvent,
        "BINDER_CONSUME" : BinderEvent,
        "SUSPEND_START" : Event,
        "SUSPEND" : Event,
        "RESUME" : Event,
        "RESUME_FINISH" : Event,
        "WAKE_LOCK" : WakeLockEvent,
        "WAKE_UNLOCK" : WakeUnlockEvent,
        "CONTEXT_SWITCH" : ContextSwitchEvent,
        "PREEMPT_TICK" : Event,
        "PREEMPT_WAKEUP" : Event,
        "YIELD" : Event,
        "IDLE_START" : Event,
        "IDLE_END" : Event,
        "FORK" : ForkEvent,
        "THREAD_NAME" : ThreadNameEvent,
        "EXIT" : Event,
        "DATAGRAM_BLOCK" : Event,
        "DATAGRAM_RESUME" : Event,
        "STREAM_BLOCK" : Event,
        "STREAM_RESUME" : Event,
        "SOCK_BLOCK" : Event,
        "SOCK_RESUME" : Event,
        "IO_BLOCK" : Event,
        "IO_RESUME" : Event,
        "WAITQUEUE_WAIT" : GeneralLockEvent,
        "WAITQUEUE_WAKE" : GeneralLockEvent,
        "WAITQUEUE_NOTIFY" : GeneralNotifyEvent,
        "MUTEX_LOCK" : GeneralLockEvent,
        "MUTEX_WAIT" : GeneralLockEvent,
        "MUTEX_WAKE" : GeneralLockEvent,
        "MUTEX_NOTIFY" : GeneralNotifyEvent,
        "SEMAPHORE_LOCK" : GeneralLockEvent,
        "SEMAPHORE_WAIT" : GeneralLockEvent,
        "SEMAPHORE_WAKE" : GeneralLockEvent,
        "SEMAPHORE_NOTIFY" : GeneralNotifyEvent,
        "FUTEX_WAIT" : GeneralLockEvent,
        "FUTEX_WAKE" : GeneralLockEvent,
        "FUTEX_NOTIFY" : GeneralNotifyEvent,
        "MSG_ENQUEUE" : MessageQueueEvent,
        "MSG_DEQUEUE" : MessageQueueEvent,
        "MSG_ENQUEUE_DELAY" : MessageQueueDelayEvent,
        "SUBMIT_ASYNC" : ExecutorEvent,
        "CONSUME_ASYNC" : ExecutorEvent,
        "SWITCH_CONFIG" : SwitchConfigEvent,
        "UI_UPDATE" : UserspaceTagEvent,
        "UI_INPUT" : UserspaceTagEvent,
        "ENTER_FOREGROUND" : UserspaceTagEvent,
        "EXIT_FOREGROUND" : UserspaceTagEvent,
        "UPLOAD_TRACE" : UserspaceTagEvent,
        "UPLOAD_DONE" : UserspaceTagEvent,
        "WRITE_TRACE" : UserspaceTagEvent,
        "WRITE_DONE" : UserspaceTagEvent,
        "MSG_POLL_NATIVE" : UserspaceTagEvent,
        "MSG_POLL_DONE" : UserspaceTagEvent
        }[data['event']](data)
    
from collections import namedtuple
EventT = namedtuple('EventT', ['event', 'timestamp', 'cpu', 'pid', 'irq', 'data'])

def decode_event_tuple(encoded):
    data = json.loads(encoded)
    timestamp = data['time']
    return EventT(data['event'],
                  timestamp['sec'] * 1000000 + timestamp['usec'],
                  data['cpu'],
                  data['pid'],
                  data['irq'],
                  data['data'])
