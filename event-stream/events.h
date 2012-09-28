#ifndef EVENTLOGGING_EVENTS_H
#define EVENTLOGGING_EVENTS_H

#include <linux/types.h>

#define EVENT_LOG_MAGIC "michigan"

#define EVENT_SYNC_LOG 0
#define EVENT_MISSED_COUNT 1

#define EVENT_CPU_ONLINE 5
#define EVENT_CPU_DOWN_PREPARE 6
#define EVENT_CPU_DEAD 7

#define EVENT_PREEMPT_WAKEUP 9
#define EVENT_CONTEXT_SWITCH 10
#define EVENT_PREEMPT_TICK 11
#define EVENT_YIELD 12

#define EVENT_IDLE_START 13
#define EVENT_IDLE_END 14
#define EVENT_FORK 15
#define EVENT_THREAD_NAME 16
#define EVENT_EXIT 17

#define EVENT_IO_BLOCK 20
#define EVENT_IO_RESUME 21

#define EVENT_DATAGRAM_BLOCK 30
#define EVENT_DATAGRAM_RESUME 31
#define EVENT_STREAM_BLOCK 32
#define EVENT_STREAM_RESUME 33
#define EVENT_SOCK_BLOCK 34
#define EVENT_SOCK_RESUME 35

#define EVENT_SEMAPHORE_LOCK 40
#define EVENT_SEMAPHORE_WAIT 41

#define EVENT_MUTEX_LOCK 50
#define EVENT_MUTEX_WAIT 51
#define EVENT_MUTEX_WAKE 52
#define EVENT_MUTEX_NOTIFY 53

#define EVENT_WAITQUEUE_WAIT 55
#define EVENT_WAITQUEUE_WAKE 56
#define EVENT_WAITQUEUE_NOTIFY 57

#define EVENT_IPC_LOCK 60
#define EVENT_IPC_WAIT 61

#define EVENT_WAKE_LOCK 70
#define EVENT_WAKE_UNLOCK 71

#define EVENT_SUSPEND_START 75
#define EVENT_SUSPEND 76
#define EVENT_RESUME 77
#define EVENT_RESUME_FINISH 78

struct event_hdr {
  __u8  event_type;
  __u8  cpu;
  __le16 pid;
  __le32 tv_sec;
  __le32 tv_usec;
}__attribute__((packed));

struct sync_log_event {
  struct event_hdr hdr;
  char magic[8];
}__attribute__((packed));

struct missed_count_event {
  struct event_hdr hdr;
  __le32 count;
}__attribute__((packed));

struct context_switch_event {
  struct event_hdr hdr;
  __le16 old_pid;
  __le16 new_pid;
  __u8   state;
  
}__attribute__((packed));

struct preempt_tick_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct preempt_wakeup_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct yield_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct hotcpu_event {
  struct event_hdr hdr;
  __u8 cpu;
}__attribute__((packed));

struct wake_lock_event {
  struct event_hdr hdr;
  __le32 lock;
  __le32 timeout;
}__attribute__((packed));

struct wake_unlock_event {
  struct event_hdr hdr;
  __le32 lock;
}__attribute__((packed));

struct suspend_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct idle_start_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct idle_end_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct fork_event {
  struct event_hdr hdr;
  __le16 pid;
  __le16 tgid;
}__attribute__((packed));

struct exit_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct thread_name_event {
  struct event_hdr hdr;
  __u16 pid;
  char comm[16];
}__attribute__((packed));

struct network_block_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct network_resume_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct waitqueue_wait_event {
  struct event_hdr hdr;
  __le32 wq;
}__attribute__((packed));

struct waitqueue_wake_event {
  struct event_hdr hdr;
  __le32 wq;
}__attribute__((packed));

struct waitqueue_notify_event {
  struct event_hdr hdr;
  __le32 wq;
  __le16 pid;
}__attribute__((packed));

struct mutex_lock_event {
  struct event_hdr hdr;
  __le32 lock;
}__attribute__((packed));

struct mutex_wait_event {
  struct event_hdr hdr;
  __le32 lock;
}__attribute__((packed));

struct mutex_wake_event {
  struct event_hdr hdr;
  __le32 lock;
}__attribute__((packed));

struct mutex_notify_event {
  struct event_hdr hdr;
  __le32 lock;
  __le16 pid;
}__attribute__((packed));

struct sem_lock_event {
  struct event_hdr hdr;
  __le32 lock;
}__attribute__((packed));

struct sem_wait_event {
  struct event_hdr hdr;
  __le32 lock;
}__attribute__((packed));

struct io_block_event {
  struct event_hdr hdr;
}__attribute__((packed));

struct io_resume_event {
  struct event_hdr hdr;
}__attribute__((packed));

#ifdef __KERNEL__

#include <linux/time.h>
#include <linux/sched.h>
#include <linux/smp.h>

#ifdef CONFIG_EVENT_LOGGING
extern void log_event(void* data, int len);

static inline void event_log_header_init(struct event_hdr* event, u8 type) {
  struct timeval tv;
  do_gettimeofday(&tv);

  event->event_type = type;
  event->tv_sec = tv.tv_sec;
  event->tv_usec = tv.tv_usec;
  event->cpu = smp_processor_id();
  event->pid = current->pid;
}

static inline void event_log_simple(u8 event_type) {
  unsigned long flags;
  struct event_hdr event;
  local_irq_save(flags);
  event_log_header_init(&event, event_type);
  log_event(&event, sizeof(struct event_hdr));
  local_irq_restore(flags);
}
#endif

static inline void event_log_context_switch(pid_t old, pid_t new, long state) {
#ifdef CONFIG_EVENT_CONTEXT_SWITCH
  unsigned long flags;
  struct context_switch_event event;
  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_CONTEXT_SWITCH);
  event.old_pid = old;
  event.new_pid = new;
  event.state = (__u8) (0x0FF & state);
  log_event(&event, sizeof(struct context_switch_event));
  local_irq_restore(flags);
#endif
}

static inline void event_log_preempt_tick(void) {
#ifdef CONFIG_EVENT_PREEMPT_TICK
  event_log_simple(EVENT_PREEMPT_TICK);
#endif
}

static inline void event_log_preempt_wakeup(void) {
#ifdef CONFIG_EVENT_PREEMPT_WAKEUP
  event_log_simple(EVENT_PREEMPT_WAKEUP);
#endif
}

static inline void event_log_yield(void) {
#ifdef CONFIG_EVENT_YIELD
  event_log_simple(EVENT_YIELD);
#endif
}

#if defined(CONFIG_EVENT_CPU_ONLINE) || defined(CONFIG_EVENT_CPU_DEAD) || defined(CONFIG_EVENT_CPU_DOWN_PREPARE)
static inline void event_log_hotcpu(unsigned int cpu, u8 event_type) {
  unsigned long flags;
  struct hotcpu_event event;
  local_irq_save(flags);
  event_log_header_init(&event.hdr, event_type);
  event.cpu = cpu;
  log_event(&event, sizeof(struct hotcpu_event));
  local_irq_restore(flags);
}
#endif

static inline void event_log_cpu_online(unsigned int cpu) {
#ifdef CONFIG_EVENT_CPU_ONLINE
  event_log_hotcpu(cpu, EVENT_CPU_ONLINE);
#endif
}

static inline void event_log_cpu_down_prepare(unsigned int cpu) {
#ifdef CONFIG_EVENT_CPU_DOWN_PREPARE
  event_log_hotcpu(cpu, EVENT_CPU_DOWN_PREPARE);
#endif
}

static inline void event_log_cpu_dead(unsigned int cpu) {
#ifdef CONFIG_EVENT_CPU_DEAD
  event_log_hotcpu(cpu, EVENT_CPU_DEAD);
#endif
}

static inline void event_log_idle_start(void) {
#ifdef CONFIG_EVENT_IDLE_START
  event_log_simple(EVENT_IDLE_START);
#endif
}

static inline void event_log_idle_end(void) {
#ifdef CONFIG_EVENT_IDLE_END
  event_log_simple(EVENT_IDLE_END);
#endif
}

static inline void event_log_suspend_start(void) {
#ifdef CONFIG_EVENT_SUSPEND_START
  event_log_simple(EVENT_SUSPEND_START);
#endif
}

static inline void event_log_suspend(void) {
#ifdef CONFIG_EVENT_SUSPEND
  event_log_simple(EVENT_SUSPEND);
#endif
}

static inline void event_log_resume(void) {
#ifdef CONFIG_EVENT_RESUME
  event_log_simple(EVENT_RESUME);
#endif
}

static inline void event_log_resume_finish(void) {
#ifdef CONFIG_EVENT_RESUME_FINISH
  event_log_simple(EVENT_RESUME_FINISH);
#endif
}

static inline void event_log_datagram_block(void) {
#ifdef CONFIG_EVENT_DATAGRAM_BLOCK
  event_log_simple(EVENT_DATAGRAM_BLOCK);
#endif
}

static inline void event_log_datagram_resume(void) {
#ifdef CONFIG_EVENT_DATAGRAM_RESUME
  event_log_simple(EVENT_DATAGRAM_RESUME);
#endif
}

static inline void event_log_stream_block(void) {
#ifdef CONFIG_EVENT_STREAM_BLOCK
  event_log_simple(EVENT_STREAM_BLOCK);
#endif
}

static inline void event_log_stream_resume(void) {
#ifdef CONFIG_EVENT_STREAM_RESUME
  event_log_simple(EVENT_STREAM_RESUME);
#endif
}

static inline void event_log_sock_block(void) {
#ifdef CONFIG_EVENT_SOCK_BLOCK
  event_log_simple(EVENT_SOCK_BLOCK);
#endif
}

static inline void event_log_sock_resume(void) {
#ifdef CONFIG_EVENT_SOCK_RESUME
  event_log_simple(EVENT_SOCK_RESUME);
#endif
}

static inline void event_log_io_block(void) {
#ifdef CONFIG_EVENT_IO_BLOCK
  event_log_simple(EVENT_IO_BLOCK);
#endif
}

static inline void event_log_io_resume(void) {
#ifdef CONFIG_EVENT_IO_RESUME
  event_log_simple(EVENT_IO_RESUME);
#endif
}

static inline void event_log_wake_lock(void* lock, long timeout) {
#ifdef CONFIG_EVENT_WAKE_LOCK
  unsigned long flags;
  struct wake_lock_event event;
  
  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_WAKE_LOCK);
  event.lock = (__le32) lock;
  event.timeout = timeout;
  log_event(&event, sizeof(struct wake_lock_event));
  local_irq_restore(flags);
#endif
}

static inline void event_log_wake_unlock(void* lock) {
  unsigned long flags;
  struct wake_unlock_event event;
  
  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_WAKE_UNLOCK);
  event.lock = (__le32) lock;
  log_event(&event, sizeof(struct wake_unlock_event));
  local_irq_restore(flags);
}

static inline void event_log_fork(pid_t pid, pid_t tgid) {
#ifdef CONFIG_EVENT_FORK
  unsigned long flags;
  struct fork_event event;
  
  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_FORK);
  event.pid = pid;
  event.tgid = tgid;
  log_event(&event, sizeof(struct fork_event));
  local_irq_restore(flags);
#endif
}

static inline void event_log_exit(void) {
#ifdef CONFIG_EVENT_EXIT
  event_log_simple(EVENT_EXIT);
#endif
}

static inline void event_log_thread_name(struct task_struct* task) {
#ifdef CONFIG_EVENT_THREAD_NAME
   unsigned long flags;
   struct thread_name_event event;
  
   local_irq_save(flags);
   event_log_header_init(&event.hdr, EVENT_THREAD_NAME);
   event.pid = task->pid;
   memcpy(event.comm, task->comm, min(16, TASK_COMM_LEN));
   log_event(&event, sizeof(struct thread_name_event));
   local_irq_restore(flags);
#endif
}

/* Can't be inlined due to #include ordering conflicts in wait.h and I
 * don't want to figure that out right now.  Can do it later, but
 * might involve a separate header file for the waitqueue events
 * or externing (instead of #including) the depedencies
 * for event_log_header_init().
 */
void event_log_waitqueue_wait(void* wq);
void event_log_waitqueue_wake(void* wq);
void event_log_waitqueue_notify(void* wq, pid_t pid);

static inline void event_log_mutex_lock(void* lock) {
#ifdef CONFIG_EVENT_MUTEX_LOCK
  unsigned long flags;
  struct mutex_lock_event event;

  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_MUTEX_LOCK);
  event.lock = (__le32) lock;
  log_event(&event, sizeof(struct mutex_lock_event));
  local_irq_restore(flags);
#endif
}

static inline void event_log_mutex_wait(void* lock) {
#ifdef CONFIG_EVENT_MUTEX_WAIT
  unsigned long flags;
  struct mutex_wait_event event;

  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_MUTEX_WAIT);
  event.lock = (__le32) lock;
  log_event(&event, sizeof(struct mutex_wait_event));
  local_irq_restore(flags);
#endif
}

static inline void event_log_mutex_wake(void* lock) {
#ifdef CONFIG_EVENT_MUTEX_WAKE
  unsigned long flags;
  struct mutex_wake_event event;
  
  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_MUTEX_WAKE);
  event.lock = (__le32) lock;
  log_event(&event, sizeof(struct mutex_wake_event));
  local_irq_restore(flags);
#endif
}

static inline void event_log_mutex_notify(void* lock, pid_t pid) {
#ifdef CONFIG_EVENT_MUTEX_WAKE
  unsigned long flags;
  struct mutex_notify_event event;
  
  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_MUTEX_NOTIFY);
  event.lock = (__le32) lock;
  event.pid = pid;
  log_event(&event, sizeof(struct mutex_notify_event));
  local_irq_restore(flags);
#endif
}

static inline void event_log_sem_lock(void* lock) {
#ifdef CONFIG_EVENT_SEMAPHORE_LOCK
  unsigned long flags;
  struct sem_lock_event event;

  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_SEMAPHORE_LOCK);
  event.lock = (__le32) lock;
  log_event(&event, sizeof(struct sem_lock_event));
  local_irq_restore(flags);
#endif
}

static inline void event_log_sem_wait(void* lock) {
#ifdef CONFIG_EVENT_SEMAPHORE_WAIT
  unsigned long flags;
  struct sem_wait_event event;

  local_irq_save(flags);
  event_log_header_init(&event.hdr, EVENT_SEMAPHORE_WAIT);
  event.lock = (__le32) lock;
  log_event(&event, sizeof(struct sem_wait_event));
  local_irq_restore(flags);
#endif
}

#endif // __KERNEL__
#endif // EVENTLOGGING_EVENTS_H
