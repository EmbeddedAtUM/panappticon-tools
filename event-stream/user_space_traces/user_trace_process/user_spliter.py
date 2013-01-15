#!/usr/bin/env python

import sys
import os
try:
	import ujson as json
except:
	import json

''' Split user space traces into monotonic increasing chunk and merge
    again based on time'''

def clock_backward(event, thread_latest):# Checks whether the timestamp is smaller than any previous event for the same pid
	cur_pid = event['pid']
	cur_timestamp = event['time']
	if(cur_pid in thread_latest):
		return thread_latest[cur_pid] > cur_timestamp
	return False	


print "Split: " + sys.argv[1]


thread_latest = {}
prev_timestamp = 0
count = 0

input_filename_split = sys.argv[1].split("/")
input_file_depth = len(input_filename_split)
#print sys.argv[1], "file depth:", input_file_depth
user_directory = input_filename_split[input_file_depth-2]
user_raw_file = input_filename_split[input_file_depth-1]

if not os.path.exists(user_directory):
	os.mkdir(user_directory)

output_filename = user_directory +"/"+ user_raw_file
output_file = open(output_filename + "_"+str(count)+".split", "w")
print "input file:" , sys.argv[1], "output file:", output_filename

input_file = open(sys.argv[1], "r")

for line in input_file:
#	print line
	event = json.loads(line)
	cur_timestamp = event['time']
	cur_pid = event['pid']
	if(cur_timestamp < prev_timestamp):# Both clock backwards and another new application could trigger this
		if(clock_backward(event, thread_latest)): # triggered by clock backwards
			print "Clock is backward for " + sys.argv[1] + " cur: ", cur_timestamp, "prev: ", prev_timestamp
			exit() # Temprorarily comment out for testing purpose
		output_file.flush()
		output_file.close()
		count += 1
		output_file = open(output_filename + "_"+str(count)+".split", "w")
	output_file.write(line)
	thread_latest[cur_pid] = cur_timestamp
	prev_timestamp = cur_timestamp

output_file.flush()
output_file.close()
