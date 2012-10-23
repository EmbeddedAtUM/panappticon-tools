#/usr/env python

import sys
import os

MSG_ENQUEUE = 0
MSG_ENQUEUE_DELAYED = 1
MSG_DEQUEUE = 2
UI_TRAVERSAL = 3
UI_INPUT = 4
EVENT_FOREGROUND = 5
EVENT_EXIT_FOREGROUND = 6
EVENT_SUBMIT_ASYNCTASK = 7
EVENT_CONSUME_ASYNCTASK = 8
EVENT_UPLOAD_TRACE = 9
EVENT_UPLOAD_DONE = 10
EVENT_WRITE_TRACE = 11
EVENT_WRITE_DONE = 12
MSG_POLL_NATIVE = 13
MSG_POLL_DONE = 14
EVENT_SWITCH_CONFIG = 15

if len(sys.argv) != 2:
	print "Usage: python user_single_trace_translate filename"
	exit()

trace_name = sys.argv[1]
print trace_name
cmd = "./parse " + trace_name + "> tmp"
os.system(cmd)
tmpfile = open("tmp","r")
for line in tmpfile:
	strline = line.strip().split()
	timestamp = strline[0]
	pid = strline[1]
	event_type = int(strline[2])
	if (event_type == MSG_ENQUEUE):
		qid = strline[3]
		mid = strline[4]
		print timestamp + "\t" + pid + "\t" + "enqueue msg "+ mid + "from queue " + qid
	elif (event_type == MSG_ENQUEUE_DELAYED):
		delayMillis = strline[3]
		print timestamp + "\t" + pid + "\t" + "enqueue delay msg " + delayMillis
	elif (event_type == MSG_DEQUEUE):
		qid = strline[3]
		mid = strline[4]
		print timestamp + "\t" + pid + "\t" + "dequeue msg " + mid + "from queue " + qid
	elif (event_type == UI_TRAVERSAL):
		print timestamp + "\t" + pid + "\t" + "UI update"
	elif (event_type == UI_INPUT):
		print >> sys.stderr, "input event"
		print timestamp + "\t" + pid + "\t" + "UI input"
	elif (event_type == EVENT_FOREGROUND):
		print timestamp + "\t" + pid + "\t" + "enter foreground"
	elif (event_type == EVENT_EXIT_FOREGROUND):
		print timestamp + "\t" + pid + "\t" + "exit foreground"
	elif (event_type == EVENT_SUBMIT_ASYNCTASK):
		runnable_code = strline[3]
		print timestamp + "\t" + pid + "\t" + "submit asynctask " + runnable_code
	elif (event_type == EVENT_CONSUME_ASYNCTASK):
		runnable_code = strline[3]
		print timestamp + "\t" + pid + "\t" + "consume asynctask " + runnable_code
	elif (event_type == EVENT_UPLOAD_TRACE):
		print timestamp + "\t" + pid + "\t" + "uploade trace"
	elif (event_type == EVENT_UPLOAD_DONE):
		print timestamp + "\t" + pid + "\t" + "uploade trace done"
	elif (event_type == EVENT_WRITE_TRACE):
		print timestamp + "\t" + pid + "\t" + "write trace to sdcard"
	elif (event_type == EVENT_WRITE_DONE):
		print timestamp + "\t" + pid + "\t" + "write trace done"
	elif (event_type == MSG_POLL_NATIVE):
		print timestamp + "\t" + pid + "\t" + "start polling native message"
	elif (event_type == MSG_POLL_DONE):
		print timestamp + "\t" + pid + "\t" + "polling native message done"
	elif (event_type == EVENT_SWITCH_CONFIG):
		config = int(strline[3])
		if (config == 0):
			strconfig = "duo core with dvfs"
		elif (config == 1):
			strconfig = "duo core without dvfs"
		elif (config == 2):
			strconfig = "single core with dvfs"
		elif (config == 3):
			strconfig = "single core withhout dvfs"
		print timestamp + "\t" + pid + "\t" + "switch to configuration "+strconfig


	
