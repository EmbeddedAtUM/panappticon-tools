#!/usr/bin/env python

import sys
try:
	import ujson as json
except:
	import json


def clock_backward(event, thread_latest):# Checks whether the timestamp is smaller than any previous event for the same pid
	cur_pid = event['pid']
	cur_timestamp = event['time']
	if(cur_pid in thread_latest):
		return thread_latest[cur_pid] > cur_timestamp
	return False	

thread_latest = {}
prev_timestamp = 0
count = 0
filename = "user/user_trace"

outputfile = open(filename + "_"+str(count), "w")
prev_timestamp = 0
for line in sys.stdin:
	event = json.loads(line)
	cur_timestamp = event['time']
	cur_pid = event['pid']
	if(cur_timestamp < prev_timestamp):# Both clock backwards and another new application could trigger this
		if(clock_backward(event, thread_latest)):
			print "Clock is backward for " + str(outputfile) + " cur: ", cur_timestamp, "prev: ", prev_timestamp
			#exit()// Temprorarily comment out for testing purpose
		outputfile.flush()
		outputfile.close()
		count += 1
		outputfile = open(filename + "_"+str(count), "w")
	outputfile.write(line)
	thread_latest[cur_pid] = cur_timestamp
	prev_timestamp = cur_timestamp

outputfile.flush()
outputfile.close()	
