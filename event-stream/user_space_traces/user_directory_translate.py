#/usr/env python

import sys
import os
import glob

path = "user/"
for infile in glob.glob(os.path.join(path, "*")):
	print infile
	outfile = "generated/" + infile + "_result"
	cmd = "python user_single_trace_translate.py "+ infile + " > "+ outfile
	os.system(cmd)
	#for line in sys.stdin.readlines():
		#print line

