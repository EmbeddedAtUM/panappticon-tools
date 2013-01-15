#!/usr/env python

def NullCHandler(evt, gState):
    pass

def time_diff(begin, end):
   return (end.timestamp - begin.timestamp).total_seconds()

def DefaultCHandler(evt, gState):
   # check to see whether there is a context_switch before
   if gState['state'] == 'Runnable_wakeup':
     gState['state'] = 'Running'
     gState['profile']['Runnable_wakeup'] += time_diff(gState['event'], evt)
   
   elif gState['state'] == 'Runnable_tick':
     gState['state'] = 'Running'
     gState['profile']['Runnable_tick'] += time_diff(gState['event'], evt)
   
   elif gState['state'] == 'Runnable_unknown':
     gState['state'] = 'Running'
     gState['profile']['Runnable_unknown'] += time_diff(gState['event'], evt)
   
   elif gState['state'] == 'Blocked':
     gState['state'] = 'Running'
     gState['profile']['Block_unknown'] += time_diff(gState['event'], evt)
   
   elif gState['state'] == 'Fork':
     gState['state'] = 'Running'
     gState['profile']['Fork'] += time_diff(gState['event'], evt)
   
   elif gState['state'] == 'Waitqueue':
     gState['state'] = 'Running'
     gState['profile']['Waitqueue'] += time_diff(gState['event'], evt)

def pair_producer_handler(evt, gState, state):
    DefaultCHandler(evt, gState)
    gState['state'] = state
    gState['event'] = evt

def pair_consumer_handler(evt, gState, state):
    # invariant: consumer is always preceded by producer
    assert(gState['state'] == state)
    gState['state'] == 'Running'
    gState['profile'][state.split('_')[0]] += time_diff(gState['event'], evt)

def wake_handler(evt, gState, bl_type):
    if(gState['state'] == 'Blocked'):
      gState['state'] = 'Running'
      gState['profile'][bl_type] += time_diff(gState['event'], evt)
    
def LockWakeCHandler(evt, gState):
    wake_handler(evt, gState, 'Lock')

def IOBlockCHandler(evt, gState):
    DefaultCHandler(evt, gState)
    gState['state'] = 'Blocked'    
    gState['event'] = evt

def IOResumeCHandler(evt, gState):
    wake_handler(evt, gState, 'IO')

def NetworkBlockCHandler(evt, gState):
    DefaultCHandler(evt, gState)
    gState['state'] = 'Blocked'
    gState['event'] = evt

def NetworkResumeCHandler(evt, gState):
    wake_handler(evt, gState, 'Network')

def BinderProduceCHandler(evt, gState):
    pair_producer_handler(evt, gState, 'Binder_block')

def BinderConsumeCHandler(evt, gState):
    pair_consumer_handler(evt, gState, 'Binder_block')

def ContextSwitchCHandler(evt, gState):
    if gState['state'] == 'Blocked':
      return        
    if evt.state == 'R':
      if gState['state'] == 'Preempt_wakeup':
        gState['state'] = 'Runnable_wakeup'
      elif gState['state'] == 'Preempt_tick':
        gState['state'] = 'Runnable_tick'
      else:
        gState['state'] = 'Runnable_unknown'

    elif evt.state == 'I' or evt.state == 'U':
      gState['state'] = 'Blocked'
    gState['event'] = evt

def ForkCHandler(evt, gState):
    #pair_producer_handler(evt, gState, 'Fork_block')
    DefaultCHandler(evt, gState)

def ForkChildCHandler(evt, gState):
    # fake fork node is treated similary as context switch
    gState['state'] = 'Fork'
    gState['event'] = evt

def EnqueueMessageCHandler(evt, gState):
    pair_producer_handler(evt, gState, 'Msg_block')

def DequeueMessageCHandler(evt, gState):
    pair_consumer_handler(evt, gState, 'Msg_block')
    msg_delay = time_diff(gState['event'], evt)
    if msg_delay > gState['profile']['Max_msg_delay']:
      gState['profile']['Max_msg_delay'] = msg_delay
    

def WaitQueueWaitCHandler(evt, gState):
    DefaultCHandler(evt, gState)

def FakeWaitQueueWakeCHandler(evt, gState):
    # fake waitqueue wake node is treated similary as context switch
    gState['state'] = 'Waitqueue'
    gState['event'] = evt

def WaitQueueWakeCHandler(evt, gState):
    if gState['state'] == 'Blocked':
      LockWakeCHandler(evt, gState)

def WaitQueueNotifyCHandler(evt, gState):
    DefaultCHandler(evt, gState)

def AsyncTaskSubmitCHandler(evt, gState):
    pair_producer_handler(evt, gState, 'Async_block')

def AsyncTaskConsumeCHandler(evt, gState):
    pair_consumer_handler(evt, gState, 'Async_block')

def UIInvalidateCHandler(evt, gState):
    pair_producer_handler(evt, gState, 'Update_block')

def UIUpdateCHandler(evt, gState):
    pair_consumer_handler(evt, gState, 'Update_block')

def UIInputCHandler(evt, gState):
    pass

def FutexWaitCHandler(evt, gState):
    DefaultCHandler(evt, gState)

def FutexWakeCHandler(evt, gState):
    if gState['state'] == 'Blocked':
      # if the preceding event is context switch
      LockWakeCHandler(evt, gState)
    else:
      # if the preceding event is futex_notify
      #assert(gState['state'] == 'Futex_notify')
      if gState['state'] == 'Futex_notify':
        gState['profile']['Futex'] += time_diff(gState['event'], evt)

def FutexNotifyCHandler(evt, gState):
    # this event should only be added by WebView related thread
    # did not add it to critical path if not
    DefaultCHandler(evt, gState)
    gState['state'] = 'Futex_notify'
    gState['event'] = evt

def PreemptWakeupCHandler(evt, gState):
    DefaultCHandler(evt, gState)
    gState['state'] = 'Preempt_wakeup'

def PreemptTickCHandler(evt, gState):
    DefaultCHandler(evt, gState)
    gState['state'] = 'Preempt_tick'
 
CountHandlerMap = {
    "BINDER_PRODUCE_ONEWAY" : BinderProduceCHandler,
    "BINDER_PRODUCE_TWOWAY" : BinderProduceCHandler,
    "BINDER_PRODUCE_REPLY" : BinderProduceCHandler,
    "BINDER_CONSUME" : BinderConsumeCHandler,
    "CONTEXT_SWITCH" : ContextSwitchCHandler,
    "PREEMPT_TICK" : PreemptTickCHandler,
    "PREEMPT_WAKEUP" : PreemptWakeupCHandler,
    "FORK" : ForkCHandler,
    "FORK_IN_CHILD" : ForkChildCHandler,
    "DATAGRAM_BLOCK" : DefaultCHandler,
    "DATAGRAM_RESUME" : NetworkResumeCHandler,
    "STREAM_BLOCK" : DefaultCHandler,
    "STREAM_RESUME" : NetworkResumeCHandler,
    "SOCK_BLOCK" : NetworkBlockCHandler,
    "SOCK_RESUME" : NetworkResumeCHandler,
    "IO_BLOCK" : DefaultCHandler,
    "IO_RESUME" : IOResumeCHandler,
    "WAITQUEUE_WAIT" : WaitQueueWaitCHandler,
    "WAITQUEUE_WAKE" : WaitQueueWakeCHandler,
    "WAITQUEUE_NOTIFY" : WaitQueueNotifyCHandler,
    "FAKED_WAITQUEUE_WAKE": FakeWaitQueueWakeCHandler,
    "MUTEX_LOCK" : DefaultCHandler,
    "MUTEX_WAIT" : DefaultCHandler,
    "MUTEX_WAKE" : LockWakeCHandler,
    "MUTEX_NOTIFY" : DefaultCHandler,
    "SEMAPHORE_LOCK" : DefaultCHandler,
    "SEMAPHORE_WAIT" : DefaultCHandler,
    "SEMAPHORE_WAKE" : LockWakeCHandler,
    "SEMAPHORE_NOTIFY" : DefaultCHandler,
    "FUTEX_WAIT" : FutexWaitCHandler,
    "FUTEX_WAKE" : FutexWakeCHandler,
    "FUTEX_NOTIFY" : FutexNotifyCHandler,
    "ENQUEUE_MSG" : EnqueueMessageCHandler,
    "DEQUEUE_MSG" : DequeueMessageCHandler,
    "DELAY_MSG" : NullCHandler,
    "SUBMIT_ASYNCTASK" : AsyncTaskSubmitCHandler,
    "CONSUME_ASYNCTASK" : AsyncTaskConsumeCHandler,
    "UI_UPDATE" : UIUpdateCHandler,
    "UI_INPUT" : UIInputCHandler,
    "UI_INVALIDATE" : UIInvalidateCHandler,
    "UI_KEY_BEGIN_BATCH": UIInputCHandler,
    "UI_KEY_CLEAR_META": UIInputCHandler,
    "UI_KEY_COMMIT_COMPLETION": UIInputCHandler,
    "UI_KEY_COMMIT_CORRECTION": UIInputCHandler,
    "UI_KEY_COMMIT_TEXT": UIInputCHandler,
    "UI_KEY_DELETE_TEXT": UIInputCHandler,
    "UI_KEY_END_BATCH": UIInputCHandler,
    "UI_KEY_FINISH_COMPOSING": UIInputCHandler,
    "UI_KEY_GET_CAPS": UIInputCHandler,
    "UI_KEY_PERFORM_EDITOR_ACTION": UIInputCHandler,
    "UI_KEY_PERFORM_CONTEXT_MENU": UIInputCHandler,
    "PREEMPT_WAKEUP": PreemptWakeupCHandler,
    "PREEMPT_TICK": PreemptTickCHandler
}
