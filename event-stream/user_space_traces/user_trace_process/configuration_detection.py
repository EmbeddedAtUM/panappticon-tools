#!/usr/bin/python

try:
	import ujson as json
except:
	import json

import sys

DVFS_OFF = 0
DVFS_ON = 1

SINGLE_CORE = 0
DUO_CORE = 1 # duo core with the hotplug management policy

'''Detect which core/dvfs configuration for event traces.
   The four configurations are:
   - DVFS on with single core
   - DVFS off with single core
   - DVFS on with dual cores
   - DVFS off with dual cores
   '''

def check_dvfs_off_event(cur_cpufreq_set):
	old_freq = cur_cpufreq_set['data']['old_khz']
	new_freq = cur_cpufreq_set['data']['new_khz']
	
	if ((old_freq == 700000) | (old_freq == 1200000)) & ((new_freq == 700000)|(new_freq == 1200000)):
		return True
	else:
		return False

def time_diff(prev_event, cur_event):
	prev_time = int(prev_event['time']['sec']) + int(prev_event['time']['usec']) * 1e-6 	
	cur_time = int(cur_event['time']['sec']) + int(cur_event['time']['usec']) * 1e-6 	
	return cur_time - prev_time

def detect_dvfs(prev_cpufreq_set, cur_cpufreq_set, cur_dvfs): 
	# if cur_cpufreq_set is 12000 - > 70000 or 70000 -> 120000 
	# and the time difference between prev and cur is bigger than 1 second
	# then it is DVFS_OFF since prev_cpufreq_set
	if (check_dvfs_off_event(cur_cpufreq_set) & check_dvfs_off_event(prev_cpufreq_set)):
		tdiff = time_diff(prev_cpufreq_set, cur_cpufreq_set)			
		if (tdiff > 1) | (cur_dvfs == SINGLE_CORE): # if it is single core already, we can ignore the time difference
			return DVFS_OFF
	return DVFS_ON
	
	

def detect_core_num(prev_cpu_dead, cur_cpu_on):
	# if the time difference between cur_cpu_on and prev_cpu_dead is less than 500 seconds
	# it is still the DUO_CORE configuration since last prev_cpu_dead
	tdiff = time_diff (prev_cpu_dead, cur_cpu_on)
	if (tdiff > 500): # 500s is the interval we manipulate the core config settings
		return SINGLE_CORE
	else:
		return DUO_CORE


def comp_Event(event1, event2):
	if (event1.timestamp > event2.timestamp):
		return 1
	elif (event1.timestamp == event2.timestamp):
		return 0
	else:
		return -1 

class Event:
	def __init__(self, event_type, time, old, new):
		self.event_type = event_type
		self.time_sec = time['sec']
		self.time_usec = time['usec']
		self.old = old
		self.new = new
		self.timestamp = float(time['sec'] + time['usec']*1e-6)
	def __str__(self):
		return "{\"event\":\""+self.event_type+"\",\"time\":{\"sec\":"+str(self.time_sec) +",\"usec\":"+str(self.time_usec)+"},\"cpu\":0,\"pid\":0,\"irq\":false,\"data\":{\"old\":" + str(self.old) +",\"new\":"+str(self.new) +"}}" 


prev_cpufreq_set = 0
prev_cpu_dead = 0

prev_core_num = -1
prev_dvfs = -1

prev_cpu_core_event = 0

switch_result = []

for line in sys.stdin:
	event = json.loads(line)
	event_type = event['event']
	pid = event['pid']
	timestamp = event['time']
		
	if (event_type == "CPUFREQ_SET"):
		set_core = event['data']['cpu']
		if set_core == 1:
			continue
		if (prev_cpufreq_set == 0):
			prev_cpufreq_set = event
		else:
			cur_dvfs = detect_dvfs(prev_cpufreq_set, event, prev_dvfs)
			if (cur_dvfs != prev_dvfs):
				if cur_dvfs == DVFS_OFF: # switch from on to off
					#print "switch DVFS from ", prev_dvfs, " to ", cur_dvfs, prev_cpufreq_set['time']
					switch_event = Event("SWITCH_DVFS", prev_cpufreq_set['time'], prev_dvfs, cur_dvfs)
					#print switch_event
					switch_result.append(switch_event)

				else: # switch from off to on
					#print "switch DVFS from ", prev_dvfs, " to ", cur_dvfs, event['time']
					switch_event = Event("SWITCH_DVFS", event['time'], prev_dvfs, cur_dvfs)
					#print switch_event
					switch_result.append(switch_event)				
	
				prev_dvfs = cur_dvfs
			prev_cpufreq_set = event

	elif (event_type == "CPU_ONLINE") | (event_type == "CPU_DEAD"):
		non_pair_flag = 0
		if (prev_cpu_core_event == 0):
			prev_cpu_core_event = event
		else:
			if (event_type == prev_cpu_core_event['event']): # these shouldn't happen
				#print "Single CPU core event !"
				#print "----------------------------"
				#print prev_cpu_core_event
				#print event 
				#print "---------------------------"
				non_pair_flag = 1
			prev_cpu_core_event = event

		if (event_type == "CPU_ONLINE"): # redundent online event is based the last online event's judgement
			if (prev_cpu_dead == 0): # no CPU_DEAD before
				cur_core_num = DUO_CORE
				switch_event = Event("SWITCH_CORE",event['time'], prev_core_num, DUO_CORE)
				switch_result.append(switch_event)

				prev_core_num = DUO_CORE
			else: 
				cur_core_num = detect_core_num(prev_cpu_dead, event)
				if (cur_core_num == SINGLE_CORE):
					switch_event = Event("SWITCH_CORE",prev_cpu_dead['time'], DUO_CORE, SINGLE_CORE)
					switch_result.append(switch_event)
					switch_event = Event("SWITCH_CORE",event['time'], SINGLE_CORE, DUO_CORE)
					
					switch_result.append(switch_event)

		elif (event_type == "CPU_DEAD"): # redundent dead event is based on the first dead event's judgement
			if non_pair_flag == 1:
				continue # do nothing for this event
			else:
				prev_cpu_dead = event

switch_result.sort(cmp=comp_Event)

for event in switch_result:
	print event
				
			
		

		
