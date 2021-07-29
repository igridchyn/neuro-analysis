#!/usr/bin/env python

# calculate mean and standard deviation of values in given columns

from sys import argv
import numpy as np

if len(argv) < 3:
	print 'USAGE (1)<input file> (2)<output file>'
	exit(0)

path = argv[1]
pfout = argv[2]


vals = [[], [], [], []]
curswr = -1
for line in open(path):
	ws = [float(f) for f in line.split(' ')]
	swri = int(ws[0])
	# only first
	if swri == curswr:
		continue
	curswr = swri
	# NORMALIZED (-ws[11) OR NOT
	vals[0].append(ws[3]-ws[11])
	vals[1].append(ws[4]-ws[11])
	vals[2].append(ws[11])
	vals[3].append(ws[3]-ws[4])

fout = open(pfout, 'w')
for i in range(4):
	fout.write('%.2f %.2f\n' % (np.nanmean(vals[i]), np.nanstd(vals[i])))
