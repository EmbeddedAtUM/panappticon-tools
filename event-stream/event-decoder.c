#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>
#include <endian.h>

#include "events.h"

#define PID_MASK 0x7FFF

char* event_to_str(int type) {
  switch (type) {
  case EVENT_SYNC_LOG:
    return "Sync";
  case EVENT_MISSED_COUNT:
    return "Missed Count";
  case EVENT_CPU_ONLINE:
    return "CPU Online";
  case EVENT_CPU_DOWN_PREPARE:
    return "CPU Down Prepare";
  case EVENT_CPU_DEAD:
    return "CPU Offline";
  case EVENT_SUSPEND_START:
    return "Suspend Start (to RAM)";
  case EVENT_SUSPEND:
    return "Suspend (to RAM)";
  case EVENT_RESUME:
    return "Resume (from RAM)";
  case EVENT_RESUME_FINISH:
    return "Resume Finish (from RAM)";
  case EVENT_WAKE_LOCK:
    return "Wake Lock";
  case EVENT_WAKE_UNLOCK:
    return "Wake Unlock";
  case EVENT_CONTEXT_SWITCH:
    return "Context Switch";
  case EVENT_PREEMPT_TICK:
    return "Preempt Tick";
  case EVENT_PREEMPT_WAKEUP:
    return "Preempt Wakeup";
  case EVENT_YIELD:
    return "Yield";
  case EVENT_IDLE_START:
    return "Idle Start";
  case EVENT_IDLE_END:
    return "Idle End";
  case EVENT_FORK:
    return "Fork";
  case EVENT_THREAD_NAME:
    return "Thread name";
  case EVENT_EXIT:
    return "Exit";
  case EVENT_DATAGRAM_BLOCK:
    return "Block (datagram)";
  case EVENT_DATAGRAM_RESUME:
    return "Resume (datagram)";
  case EVENT_STREAM_BLOCK:
    return "Block (stream)";
  case EVENT_STREAM_RESUME:
    return "Resume (stream)";
  case EVENT_SOCK_BLOCK:
    return "Block (socket)";
  case EVENT_SOCK_RESUME:
    return "Resume (socket)";
  case EVENT_WAITQUEUE_WAIT:
    return "Wait (waitqueue)";
  case EVENT_WAITQUEUE_WAKE:
    return "Wake (waitqueue)";
  case EVENT_WAITQUEUE_NOTIFY:
    return "Notify (waitqueue)";
  case EVENT_MUTEX_LOCK:
    return "Lock (mutex)";
  case EVENT_MUTEX_WAIT:
    return "Wait (mutex)";
  case EVENT_MUTEX_WAKE:
    return "Wake (mutex)";
  case EVENT_MUTEX_NOTIFY:
    return "Notify (mutex)";
  case EVENT_SEMAPHORE_LOCK:
    return "Lock (sem)";
  case EVENT_SEMAPHORE_WAIT:
    return "Wait (sem)";
  case EVENT_IO_BLOCK:
    return "Block (IO)";
  case EVENT_IO_RESUME:
    return "Resume (IO)";
  default:
    return "Unknown";
  }
}

char* TASK_STATE[] = {"Running", "Interruptible", "Uninterruptible", "Stopped", "Traced", NULL, NULL, "Dead", "Wakekill"};

static inline size_t read_next_header(struct event_hdr* header, FILE* stream) {
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

void process_simple_event(FILE* stream) {
  printf("\n");
}

void process_general_lock_event(FILE* stream) {
  struct general_lock_event event;
  fread(&event.lock, 4, 1, stream);
  printf(" [%0x]\n", event.lock);
}

void process_general_notify_event(FILE* stream) {
  struct general_notify_event event;
  fread(&event.lock, 4, 1, stream);
  fread(&event.pid, 2, 1, stream);
  printf(" [%0x] pid: %d\n", event.lock, event.pid);
}

void process_sync_log_event(FILE* stream) {
  struct sync_log_event event;
  fread(&event.magic, 8, 1, stream);
  printf(" %8s\n", event.magic);
}

void process_missed_count_event(FILE* stream) {
  struct missed_count_event event;
  fread(&event.count, 4, 1, stdin);
  printf(" %d\n", event.count);
}

void process_hotcpu_event(FILE* stream) {
  struct hotcpu_event event;
  fread(&event.cpu, 1, 1, stdin);
  printf(": %d\n", event.cpu);
}

void process_context_switch_event(struct event_hdr * header, FILE* stream) {
  struct context_switch_event event;
  fread(&event.new_pid, 2, 1, stdin);
  fread(&event.state, 1, 1, stdin);
  printf("%5d => %5d (%s)\n", header->pid, event.new_pid, TASK_STATE[event.state ? __builtin_ctz(event.state)+1 : 0]);
}

void process_wake_lock_event(FILE* stream) {
  struct wake_lock_event event;
  fread(&event.lock, 4, 1, stdin);
  fread(&event.timeout, 4, 1, stdin);
  printf("[%x]", event.lock);
  if (event.timeout != 0)
    printf(" (%d)", event.timeout);
  printf("\n");
}

void process_wake_unlock_event(FILE* stream) {
  struct wake_unlock_event event;
  fread(&event.lock, 4, 1, stdin);
  printf("[%x]\n", event.lock);
}

void process_fork_event(FILE* stream) {
  struct fork_event event;
  fread(&event.pid, 4, 1, stdin);
  printf("pid:%d tgid:%d\n", event.pid, event.tgid);
}						   

void process_thread_name_event(FILE* stream) {
  struct thread_name_event event;
  fread(&event.pid, 2, 1, stdin);
  fread(&event.comm, 16, 1, stdin);
  printf("%d=>\"%s\"\n", event.pid, event.comm);
}

int main() {
  struct event_hdr header;
  struct timeval timestamp;

  FILE* stream = stdin;

  while (read_next_header(&header, stream) && !feof(stream)) {
    read_next_timestamp(&timestamp, &header, stdin);

    print_event_common(&header, &timestamp);
    
    switch (header.event_type) {
    case EVENT_SYNC_LOG:
      process_sync_log_event(stream);
      break;
    case EVENT_MISSED_COUNT:
      process_missed_count_event(stream);
      break;
    case EVENT_CPU_ONLINE:
    case EVENT_CPU_DOWN_PREPARE:
    case EVENT_CPU_DEAD:
      process_hotcpu_event(stream);
      break;
    case EVENT_THREAD_NAME:
      process_thread_name_event(stream);
      break;
    case EVENT_CONTEXT_SWITCH:
      process_context_switch_event(&header, stream);
      break;
    case EVENT_WAKE_LOCK:
      process_wake_lock_event(stream);
      break;
    case EVENT_WAKE_UNLOCK:
      process_wake_unlock_event(stream);
      break;
    case EVENT_FORK:
      process_fork_event(stream);
      break;
    case EVENT_EXIT:
      process_simple_event(stream);
      break;
    case EVENT_WAITQUEUE_WAIT:
    case EVENT_WAITQUEUE_WAKE:
    case EVENT_MUTEX_LOCK:
    case EVENT_MUTEX_WAIT:
    case EVENT_MUTEX_WAKE:
    case EVENT_SEMAPHORE_LOCK:
    case EVENT_SEMAPHORE_WAIT:
      process_general_lock_event(stream);
      break;
    case EVENT_WAITQUEUE_NOTIFY:
    case EVENT_MUTEX_NOTIFY:
      process_general_notify_event(stream);
      break;
    case EVENT_PREEMPT_TICK:
    case EVENT_PREEMPT_WAKEUP:
    case EVENT_YIELD:
    case EVENT_SUSPEND_START:
    case EVENT_SUSPEND:
    case EVENT_RESUME:
    case EVENT_RESUME_FINISH:
    case EVENT_IDLE_START:
    case EVENT_IDLE_END:
    case EVENT_DATAGRAM_BLOCK:
    case EVENT_DATAGRAM_RESUME:
    case EVENT_STREAM_BLOCK:
    case EVENT_STREAM_RESUME:
    case EVENT_SOCK_BLOCK:
    case EVENT_SOCK_RESUME:
    case EVENT_IO_BLOCK:
    case EVENT_IO_RESUME:
      process_simple_event(stream);
      break;
    default:
      printf("Unknown event type received: %d\n", header.event_type);
    }
  }

 }
