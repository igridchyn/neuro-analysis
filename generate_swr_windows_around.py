#!/usr/bin/env python

from sys import argv
from iutils import *

if len(argv) < 5:
	print 'USAGE: <1>(input swr timestamps)  <2>(ms before) <3>(ms after) <4>(output - start-peak-end swrs)'
	print 'GENERATE SWR TIMESTAMPS IN BEGINNING-PEAK-END FORMAT WITH GIVEN NUMBER OF SPIKES BEFORE AND AFTER THE PEAK'
	exit(0)

argv = resolve_vars(argv)

ts = []
for line in open(argv[1]):
	ts.append(int(line))

MSBEF = int(round(float(argv[2])))
MSAFT = int(round(float(argv[3])))
fout = open(argv[4], 'w')
for t in ts:
	fout.write('%d %d %d\n' % (t-MSBEF*24, t, t+MSAFT*24))
fout.close()
