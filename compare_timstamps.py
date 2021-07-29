#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

if len(argv) < 3:
	print 'USAGE: (1)<ts file 1 - ripples> (2)<ts file 2 - sync>'
	exit(0)

ts1 = np.loadtxt(argv[1]) + 154
ts2 = np.loadtxt(argv[2])

if len(ts1.shape) > 1:
	ts1 = ts1[:,1]
	print 'Take 2nd column of ts1'

if len(ts2.shape) > 1:
	ts2 = ts2[:,1]
	print 'Take 2nd column of ts2'

i1 = 0
i2 = 0

# time window, within which detections are considered to represent the same event
samewin = 2400

# calculate: delay between detections of the same event
# number of events detected

nmatch = 0
totdelay = 0

for i in range(len(ts1)):
	diffs = ts2 - ts1[i]
	iclosest = np.argmin(np.abs(diffs))

	if abs(diffs[iclosest]) < samewin:
		nmatch += 1
		totdelay += diffs[iclosest]

print '%d events from ts1 were also in ts2 (within %d), mean delay = %.2f' % (nmatch, samewin, totdelay / float(nmatch))
