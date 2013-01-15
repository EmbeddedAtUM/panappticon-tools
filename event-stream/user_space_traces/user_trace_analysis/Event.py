#!/usr/bin/env python

import datetime as dt
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
        self.json = data
        self.thread_name = ''
        self.node_id = ''
        self.core = 1 # 1: duo; 0: single
        self.dvfs = 1 # 1: dvfs on; 0: off

    def __str__(self):
        thread_name = self.pid if len(self.thread_name) == 0 else self.thread_name
#        return "[%s] <%s> (%24s) %16s %s"%(format_timestamp(self.timestamp),
#                                        self.cpu,
#                                        "I %5s"%thread_name if self.irq else thread_name,
#                                        self.event.replace('_',' ').capitalize(), self.node_id)
        return "[%s.%s] <%s> (%24s) %16s %s %s %s"%(self.timestamp.strftime('%s'), self.timestamp.strftime('%f'),
                                self.cpu,
                                "I %5s"%thread_name if self.irq else thread_name,
                                self.event.replace('_',' ').capitalize(), self.node_id,
                                'Duo' if self.core == 1 else 'Single',
                                'DVFS_on' if self.dvfs == 1 else 'DVFS_off')

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
        header = super(SyncLogEvent, self).__str__()
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
        return "%s: %d" % (header, self.transaction)

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

class UserspaceEvent(Event):
    def __init__(self, data):
        data['cpu'] = 9
        data['irq'] = False
        super(UserspaceEvent, self).__init__(data)

class MessageQueueEvent(UserspaceEvent):
    def __init__(self, data):
        super(MessageQueueEvent, self).__init__(data)
        self.message_id = self.data['message_id']
        self.queue_id = self.data['queue_id']

    def __str__(self):
        header = super(MessageQueueEvent, self).__str__()
        return "%s: Message: %3d Queue: %3d"%(header, self.message_id, self.queue_id)


class MessageQueueDelayEvent(UserspaceEvent):
    def __init__(self, data):
        super(MessageQueueDelayEvent, self).__init__(data)
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
        "ENQUEUE_MSG" : MessageQueueEvent,
        "DEQUEUE_MSG" : MessageQueueEvent,
        "DELAY_MSG" : MessageQueueDelayEvent,
        "SUBMIT_ASYNCTASK" : ExecutorEvent,
        "CONSUME_ASYNCTASK" : ExecutorEvent,
        "SWITCH_CONFIG" : SwitchConfigEvent,
        "UI_UPDATE" : UserspaceTagEvent,
        "UI_INPUT" : UserspaceTagEvent,
        "UI_KEY_BEGIN_BATCH": UserspaceTagEvent,
        "UI_KEY_CLEAR_META": UserspaceTagEvent,
        "UI_KEY_COMMIT_COMPLETION": UserspaceTagEvent,
        "UI_KEY_COMMIT_CORRECTION": UserspaceTagEvent,
        "UI_KEY_COMMIT_TEXT": UserspaceTagEvent,
        "UI_KEY_DELETE_TEXT": UserspaceTagEvent,
        "UI_KEY_END_BATCH": UserspaceTagEvent,
        "UI_KEY_FINISH_COMPOSING": UserspaceTagEvent,
        "UI_KEY_GET_CAPS": UserspaceTagEvent,
        "UI_KEY_PERFORM_EDITOR_ACTION": UserspaceTagEvent,
        "UI_KEY_PERFORM_CONTEXT_MENU": UserspaceTagEvent,
        "UI_KEY_PERFORM_PRIVATE_COMMAND": UserspaceTagEvent,
        "UI_KEY_SET_COMPOSING_TEXT": UserspaceTagEvent,
        "UI_KEY_SET_COMPOSING_REGION": UserspaceTagEvent,
        "UI_KEY_SET_SELECTION": UserspaceTagEvent,
        "UI_KEY_SEND_KEY": UserspaceTagEvent,
        "UI_KEY_GET_TEXT_AFTER": UserspaceTagEvent,
        "UI_KEY_GET_TEXT_BEFORE": UserspaceTagEvent,
        "UI_KEY_GET_SELECTED_TEXT": UserspaceTagEvent,
        "UI_KEY_GET_EXTRACTED_TEXT": UserspaceTagEvent,
        "ENTER_FOREGROUND" : UserspaceTagEvent,
        "EXIT_FOREGROUND" : UserspaceTagEvent,
        "UPLOAD_TRACE" : UserspaceTagEvent,
        "UPLOAD_DONE" : UserspaceTagEvent,
        "WRITE_TRACE" : UserspaceTagEvent,
        "WRITE_DONE" : UserspaceTagEvent,
        "MSG_POLL_NATIVE" : UserspaceTagEvent,
        "MSG_POLL_DONE" : UserspaceTagEvent,
        "UI_INVALIDATE": UserspaceTagEvent,
        "UI_KEY_FINISH_COMPOSING": UserspaceTagEvent,
        "UI_UPDATE_VSYNC": UserspaceTagEvent,
        "UI_UPDATE_DISPATCH": UserspaceTagEvent,
        "EVENT_OPENGL": UserspaceTagEvent,
        "BROKEN_LOG_START": UserspaceTagEvent,
        "BROKEN_LOG_END": UserspaceTagEvent,
        "SWITCH_CORE": UserspaceTagEvent,
        "SWITCH_DVFS": UserspaceTagEvent
        }[data['event']](data)

def main(istream, ostream):
    for line in istream:
        event = decode_event(line)
        print(event)

if __name__ == "__main__":
    import sys

    istream = sys.stdin
    ostream = sys.stdout

    main(istream, ostream)
