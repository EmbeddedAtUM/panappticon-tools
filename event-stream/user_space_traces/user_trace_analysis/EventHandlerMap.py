from EventHandlers import *

event_handler_map = {
    "SYNC_LOG" : NullHandler,
    "MISSED_COUNT" : NullHandler,
    "CPU_ONLINE" : NullHandler,
    "CPU_DOWN_PREPARE" : NullHandler,
    "CPU_DEAD" : NullHandler,
    "CPUFREQ_SET" : NullHandler,
    "BINDER_PRODUCE_ONEWAY" : BinderOneWayProduceHandler,
    "BINDER_PRODUCE_TWOWAY" : BinderTwoWayProduceHandler,
    "BINDER_PRODUCE_REPLY" : BinderReplyHandler,
    "BINDER_CONSUME" : BinderConsumeHandler,
    "SUSPEND_START" : NullHandler,
    "SUSPEND" : NullHandler,
    "RESUME" : NullHandler,
    "RESUME_FINISH" : NullHandler,
    "WAKE_LOCK" : NullHandler,
    "WAKE_UNLOCK" : NullHandler,
    "CONTEXT_SWITCH" : ContextSwitchHandler,
    "PREEMPT_TICK" : DefaultHandler,
    "PREEMPT_WAKEUP" : DefaultHandler,
    "YIELD" : NullHandler,
    "IDLE_START" : NullHandler,
    "IDLE_END" : NullHandler,
    "FORK" : ForkHandler,
    "THREAD_NAME" : ThreadNameHandler,
    "EXIT" : NullHandler,
    "DATAGRAM_BLOCK" : DefaultHandler,
    "DATAGRAM_RESUME" : DefaultHandler,
    "STREAM_BLOCK" : DefaultHandler,
    "STREAM_RESUME" : DefaultHandler,
    "SOCK_BLOCK" : DefaultHandler,
    "SOCK_RESUME" : DefaultHandler,
    "IO_BLOCK" : DefaultHandler,
    "IO_RESUME" : DefaultHandler,
    "WAITQUEUE_WAIT" : WaitQueueWaitHandler,
    "WAITQUEUE_WAKE" : WaitQueueWakeHandler,
    "WAITQUEUE_NOTIFY" : WaitQueueNotifyHandler,
    "MUTEX_LOCK" : DefaultHandler,
    "MUTEX_WAIT" : DefaultHandler,
    "MUTEX_WAKE" : DefaultHandler,
    "MUTEX_NOTIFY" : DefaultHandler,
    "SEMAPHORE_LOCK" : DefaultHandler,
    "SEMAPHORE_WAIT" : DefaultHandler,
    "SEMAPHORE_WAKE" : DefaultHandler,
    "SEMAPHORE_NOTIFY" : DefaultHandler,
    "FUTEX_WAIT" : FutexWaitHandler,
    "FUTEX_WAKE" : FutexWakeHandler,
    "FUTEX_NOTIFY" : FutexNotifyHandler,
    "ENQUEUE_MSG" : EnqueueMessageHandler,
    "DEQUEUE_MSG" : DequeueMessageHandler,
    "DELAY_MSG" : NullHandler,
    "SUBMIT_ASYNCTASK" : AsyncTaskSubmitHandler,
    "CONSUME_ASYNCTASK" : AsyncTaskConsumeHandler,
    "SWITCH_CONFIG" : NullHandler,
    "UI_UPDATE" : UIUpdateV2Handler,
    "UI_INPUT" : UIInputHandler,
    "UI_KEY_BEGIN_BATCH": UIInputHandler,
    "UI_KEY_CLEAR_META": UIInputHandler,
    "UI_KEY_COMMIT_COMPLETION": UIInputHandler,
    "UI_KEY_COMMIT_CORRECTION": UIInputHandler,
    "UI_KEY_COMMIT_TEXT": UIInputHandler,
    "UI_KEY_DELETE_TEXT": UIInputHandler,
    "UI_KEY_END_BATCH": UIInputHandler,
    "UI_KEY_FINISH_COMPOSING": UIInputHandler,
    "UI_KEY_GET_CAPS": UIInputHandler,
    "UI_KEY_PERFORM_EDITOR_ACTION": UIInputHandler,
    "UI_KEY_PERFORM_CONTEXT_MENU": UIInputHandler,
    "UI_KEY_PERFORM_PRIVATE_COMMAND": UIInputHandler,
    "UI_KEY_SET_COMPOSING_TEXT": UIInputHandler,
    "UI_KEY_SET_COMPOSING_REGION": UIInputHandler,
    "UI_KEY_SET_SELECTION": UIInputHandler,
    "UI_KEY_SEND_KEY": UIInputHandler,
    "UI_KEY_GET_TEXT_AFTER": UIInputHandler,
    "UI_KEY_GET_TEXT_BEFORE": UIInputHandler,
    "UI_KEY_GET_SELECTED_TEXT": UIInputHandler,
    "UI_KEY_GET_EXTRACTED_TEXT": UIInputHandler,
    "UI_KEY_FINISH_COMPOSING": UIInputHandler,
    "ENTER_FOREGROUND" : EnterForegroundHandler,
    "EXIT_FOREGROUND" : ExitForegroundHandler,
    "UPLOAD_TRACE" : NullHandler,
    "UPLOAD_DONE" : NullHandler,
    "WRITE_TRACE" : NullHandler,
    "WRITE_DONE" : NullHandler,
    "MSG_POLL_NATIVE" : PollNativeHandler,
    "MSG_POLL_DONE" : PollDoneHandler,
    "UI_INVALIDATE": UIInvalidateV2Handler,
    "UI_UPDATE_VSYNC": NullHandler,
    "UI_UPDATE_DISPATCH": NullHandler,
    "EVENT_OPENGL": NullHandler,
    "BROKEN_LOG_START": NullHandler,
    "BROKEN_LOG_END": NullHandler,
    "SWITCH_CORE": CoreConfigChangeHandler,
    "SWITCH_DVFS": DVFSConfigChangeHandler}
