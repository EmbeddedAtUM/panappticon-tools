#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>
#include <endian.h>

#include "events.h"

#define PID_MASK 0x7FFF

static const char* const event_strings[256] = {
  [EVENT_SYNC_LOG] = "Sync",
  [EVENT_MISSED_COUNT] = "Missed Count",
  [EVENT_CPU_ONLINE] = "CPU Online",
  [EVENT_CPU_DOWN_PREPARE] = "CPU Down Prepare",
  [EVENT_CPU_DEAD] = "CPU Offline",
  [EVENT_SUSPEND_START] = "Suspend Start (to RAM)",
  [EVENT_SUSPEND] = "Suspend (to RAM)",
  [EVENT_RESUME] = "Resume (from RAM)",
  [EVENT_RESUME_FINISH] = "Resume Finish (from RAM)",
  [EVENT_WAKE_LOCK] = "Wake Lock",
  [EVENT_WAKE_UNLOCK] = "Wake Unlock",
  [EVENT_CONTEXT_SWITCH] = "Context Switch",
  [EVENT_PREEMPT_TICK] = "Preempt Tick",
  [EVENT_PREEMPT_WAKEUP] = "Preempt Wakeup",
  [EVENT_YIELD] = "Yield",
  [EVENT_IDLE_START] = "Idle Start",
  [EVENT_IDLE_END] = "Idle End",
  [EVENT_FORK] = "Fork",
  [EVENT_THREAD_NAME] = "Thread name",
  [EVENT_EXIT] = "Exit",
  [EVENT_DATAGRAM_BLOCK] = "Block (datagram)",
  [EVENT_DATAGRAM_RESUME] = "Resume (datagram)",
  [EVENT_STREAM_BLOCK] = "Block (stream)",
  [EVENT_STREAM_RESUME] = "Resume (stream)",
  [EVENT_SOCK_BLOCK] = "Block (socket)",
  [EVENT_SOCK_RESUME] = "Resume (socket)",
  [EVENT_WAITQUEUE_WAIT] = "Wait (waitqueue)",
  [EVENT_WAITQUEUE_WAKE] = "Wake (waitqueue)",
  [EVENT_WAITQUEUE_NOTIFY] = "Notify (waitqueue)",
  [EVENT_MUTEX_LOCK] = "Lock (mutex)",
  [EVENT_MUTEX_WAIT] = "Wait (mutex)",
  [EVENT_MUTEX_WAKE] = "Wake (mutex)",
  [EVENT_MUTEX_NOTIFY] = "Notify (mutex)",
  [EVENT_SEMAPHORE_LOCK] = "Lock (sem)",
  [EVENT_SEMAPHORE_WAIT] = "Wait (sem)",
  [EVENT_SEMAPHORE_NOTIFY] = "Notify (sem)",
  [EVENT_SEMAPHORE_WAKE] = "Wake (sem)",
  [EVENT_FUTEX_WAIT] = "Wait (futex)",
  [EVENT_FUTEX_WAKE] = "Wake (futex)",
  [EVENT_FUTEX_NOTIFY] = "Notify (futex)",
  [EVENT_IO_BLOCK] = "Block (IO)",
  [EVENT_IO_RESUME] = "Resume (IO)",
  "Unknown"
};

static inline const char* event_to_str(const int type) {
  return event_strings[type];
}

char* TASK_STATE[] = {"Running", "Interruptible", "Uninterruptible", "Stopped", "Traced", NULL, NULL, "Dead", "Wakekill"};

inline size_t read_next_header(struct event_hdr* header, FILE* stream) {
  return fread(header, sizeof(*header), 1, stream);
}

// From http://graphics.stanford.edu/~seander/bithacks.html#FixedSignExtend
#define SIGN_EXT(val, b) ((val ^ (1 << (b-1))) - (1 << (b-1)))

/* Only works on little endian arch */
static inline void read_next_timestamp(struct timeval* tv, struct event_hdr* header, FILE* stream) {
  static struct timeval prev;

  int sec_len;
  int usec_len;
  tv->tv_sec = 0;
  tv->tv_usec = 0;

  sec_len = GET_SEC_LEN(header);
  usec_len = GET_USEC_LEN(header);

  fread(&tv->tv_sec, 1, sec_len, stream);
  fread(&tv->tv_usec, 1, usec_len, stream);

  tv->tv_sec = SIGN_EXT(tv->tv_sec, sec_len*8);
  tv->tv_usec = SIGN_EXT(tv->tv_usec, usec_len*8);

  if (header->event_type == EVENT_SYNC_LOG) {
    prev = *tv;
  }
  else {
    prev.tv_sec += tv->tv_sec;
    prev.tv_usec += tv->tv_usec;
    *tv = prev;
  }

}

void print_event_common(struct event_hdr* header, struct timeval* tv) {
  time_t time = tv->tv_sec;
  struct tm *time_tm = localtime(&time);

  char tmbuf[64], buf[64];
  strftime(tmbuf, sizeof tmbuf, "%Y-%m-%d %H:%M:%S", time_tm);
  snprintf(buf, sizeof buf, "%s.%06d", tmbuf, tv->tv_usec);

  if (0x8000 & header->pid)
    printf("[%s] <%d> (I %5d) %s ", buf, GET_CPU(header), header->pid & PID_MASK, event_to_str(header->event_type));
  else
    printf("[%s] <%d> (%7d) %s ", buf, GET_CPU(header), header->pid & PID_MASK, event_to_str(header->event_type));
}

void process_simple_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  printf("\n");
}

void process_general_lock_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct general_lock_event event;
  fread(&event.lock, 4, 1, stream);
  printf(" [%0x]\n", event.lock);
}

void process_general_notify_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct general_notify_event event;
  fread(&event.lock, 4, 1, stream);
  fread(&event.pid, 2, 1, stream);
  printf(" [%0x] pid: %d\n", event.lock, event.pid);
}

void process_sync_log_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct sync_log_event event;
  fread(&event.magic, 8, 1, stream);
  printf(" %8s\n", event.magic);
}

void process_missed_count_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct missed_count_event event;
  fread(&event.count, 4, 1, stdin);
  printf(" %d\n", event.count);
}

void process_hotcpu_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct hotcpu_event event;
  fread(&event.cpu, 1, 1, stdin);
  printf(": %d\n", event.cpu);
}

void process_context_switch_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct context_switch_event event;
  fread(&event.new_pid, 2, 1, stdin);
  fread(&event.state, 1, 1, stdin);
  printf("%5d => %5d (%s)\n", header->pid, event.new_pid, TASK_STATE[event.state ? __builtin_ctz(event.state)+1 : 0]);
}

void process_wake_lock_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct wake_lock_event event;
  fread(&event.lock, 4, 1, stdin);
  fread(&event.timeout, 4, 1, stdin);
  printf("[%x]", event.lock);
  if (event.timeout != 0)
    printf(" (%d)", event.timeout);
  printf("\n");
}

void process_wake_unlock_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct wake_unlock_event event;
  fread(&event.lock, 4, 1, stdin);
  printf("[%x]\n", event.lock);
}

void process_fork_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct fork_event event;
  fread(&event.pid, 4, 1, stdin);
  printf("pid:%d tgid:%d\n", event.pid, event.tgid);
}						   

void process_thread_name_event(FILE* stream, struct event_hdr* header, struct timeval* tv) {
  struct thread_name_event event;
  fread(&event.pid, 2, 1, stdin);
  fread(&event.comm, 16, 1, stdin);
  printf("%d=>\"%s\"\n", event.pid, event.comm);
}

typedef void (*decode_event_func)(FILE* stream, struct event_hdr* header, struct timeval* tv);

static decode_event_func decoders[256] = {
  [EVENT_SYNC_LOG]		= process_sync_log_event,
  [EVENT_MISSED_COUNT]		= process_missed_count_event,
  [EVENT_CPU_ONLINE]		= process_hotcpu_event,
  [EVENT_CPU_DOWN_PREPARE]	= process_hotcpu_event,
  [EVENT_CPU_DEAD]		= process_hotcpu_event,
  [EVENT_THREAD_NAME]		= process_thread_name_event,
  [EVENT_CONTEXT_SWITCH]	= process_context_switch_event,
  [EVENT_WAKE_LOCK]		= process_wake_lock_event,
  [EVENT_WAKE_UNLOCK]		= process_wake_unlock_event,
  [EVENT_FORK]			= process_fork_event,
  [EVENT_WAITQUEUE_WAIT]	= process_general_lock_event,
  [EVENT_WAITQUEUE_WAKE]	= process_general_lock_event,
  [EVENT_MUTEX_LOCK]		= process_general_lock_event,
  [EVENT_MUTEX_WAIT]		= process_general_lock_event,
  [EVENT_MUTEX_WAKE]		= process_general_lock_event,
  [EVENT_SEMAPHORE_LOCK]	= process_general_lock_event,
  [EVENT_SEMAPHORE_WAIT]	= process_general_lock_event,
  [EVENT_SEMAPHORE_WAKE]	= process_general_lock_event,
  [EVENT_FUTEX_WAIT]		= process_general_lock_event,
  [EVENT_FUTEX_WAKE]		= process_general_lock_event,
  [EVENT_WAITQUEUE_NOTIFY]	= process_general_notify_event,
  [EVENT_MUTEX_NOTIFY]		= process_general_notify_event,
  [EVENT_SEMAPHORE_NOTIFY]	= process_general_notify_event,
  [EVENT_FUTEX_NOTIFY]		= process_general_notify_event,
  [EVENT_EXIT]			= process_simple_event,
  [EVENT_PREEMPT_TICK]		= process_simple_event,
  [EVENT_PREEMPT_WAKEUP]	= process_simple_event,
  [EVENT_YIELD]			= process_simple_event,
  [EVENT_SUSPEND_START]		= process_simple_event,
  [EVENT_SUSPEND]		= process_simple_event,
  [EVENT_RESUME]		= process_simple_event,
  [EVENT_RESUME_FINISH]		= process_simple_event,
  [EVENT_IDLE_START]		= process_simple_event,
  [EVENT_IDLE_END]		= process_simple_event,
  [EVENT_DATAGRAM_BLOCK]	= process_simple_event,
  [EVENT_DATAGRAM_RESUME]	= process_simple_event,
  [EVENT_STREAM_BLOCK]		= process_simple_event,
  [EVENT_STREAM_RESUME]		= process_simple_event,
  [EVENT_SOCK_BLOCK]		= process_simple_event,
  [EVENT_SOCK_RESUME]		= process_simple_event,
  [EVENT_IO_BLOCK]		= process_simple_event,
  [EVENT_IO_RESUME]		= process_simple_event,
  NULL
};

int main() {
  decode_event_func decoder;
  struct event_hdr header;
  struct timeval timestamp;

  FILE* stream = stdin;

  while (read_next_header(&header, stream) && !feof(stream)) {
    read_next_timestamp(&timestamp, &header, stdin);
    print_event_common(&header, &timestamp);
    
    decoder = decoders[header.event_type];
    if (!decoder) {
      fprintf(stderr, "Unknown event type received: %d\n", header.event_type);
      exit(1);
    }

    decoder(stream, &header, &timestamp);
  }
 }
