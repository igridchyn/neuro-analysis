#!/usr/bin/env python

from sys import argv
from iutils import *

if len(argv) < 7:
	print 'USAGE: <1>(input swr timestamps) <2>(total res) <3>(number of spikes before) <4>(number of spikes after) <5>(output - start-peak-end swrs) <6>(limit on the duration, ms)'
	print 'GENERATE SWR TIMESTAMPS IN BEGINNING-PEAK-END FORMAT WITH GIVEN NUMBER OF SPIKES BEFORE AND AFTER THE PEAK'
	exit(0)

argv = resolve_vars(argv)

ts = []
for line in open(argv[1]):
	ts.append(int(line))

res = []
for line in open(argv[2]):
	res.append(int(line))

SPBEF = int(round(float(argv[3])))
SPAFT = int(round(float(argv[4])))

LDUR = int(argv[6]) * 24

fts = []
ires = 0
LR = len(res)
fout = open(argv[5], 'w')

istartprev = 0

c = 0
for t in ts:
	while ires < LR and res[ires] < t:
		ires += 1

	istart = max(0, ires - SPBEF)
	iend = min(ires + SPAFT, len(res) - 1)

	if LDUR == 0 or res[iend]-res[istart] < LDUR and (istart != istartprev):
		fout.write('%d %d %d\n' % (res[istart], t, res[iend]))
		c += 1

	istartprev = istart
fout.close()

print 'Done, number of events included: %d' % c
