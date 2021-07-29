#!/usr/bin/env python

import os
from sys import argv
from tracking_processing import *
from matplotlib import pyplot as plt

if len(argv) < 7:
	print 'Usage: (1)<whl file> (2)<start box X> (3)<start box Y> (4)<start box radius> (5)<minimal time to be outside the SB> (6)<minimal time inside the radius>'
	print 'Plotting trajectories and witing intervals when animal was far from given point at a given distance for at least given time'
	print 'Leaving the radius -> trial started'
	exit(0)

# whl = whl_to_pos(open(argv[1]), False, -1)
# short format
whl = [[float(w.split(' ')[0]), float(w.split(' ')[1])] for w in open(argv[1]) if len(w) > 0]

sbx = float(argv[2])
sby = float(argv[3])
sbrad = float(argv[4])
# minimal time to be outside of the SB
mint = float(argv[5])
minti = float(argv[6])

sb = [sbx, sby]
i = 0
trials = []
inside = True
tout = 0
tstart = 0
tin = 0
entry = 0
while i < len(whl):
	if whl[i][0] < 0:
		i +=1
		continue

	if inside:
		if distance(sb, whl[i]) > sbrad:
			inside = False
			tstart = i
			tin = 0
	else:
		if distance(sb, whl[i]) < sbrad:
			if tin == 0:
				entry = i	
			
			tin += 1

			if tin > minti:
				inside = True
				if i - tstart >= mint:
					trials.append([tstart, entry])
		else:
			tin = 0

	i += 1

print trials

px = 3
py = 5
f, axarr = plt.subplots(px, py)

i = 0
sub = 0
ptrial = [0, 1]
for trial in trials:
	btrial = [ptrial[1], trial[0]]
	axarr[i % px, (i - sub) / px].plot([w[0] for w in whl[trial[0]:trial[1]] if w[0] > 0], [w[1] for w in whl[trial[0]:trial[1]] if w[1] > 0])
	axarr[i % px, (i - sub) / px].plot([w[0] for w in whl[btrial[0]:btrial[1]] if w[0] > 0], [w[1] for w in whl[btrial[0]:btrial[1]] if w[1] > 0], color = 'r')
	i += 1
	if i >= px * py + sub:
		print 'WARNING: not all trials shown!'
		plt.suptitle(argv[1])
		plt.show()
		f, axarr = plt.subplots(px, py)
		sub += py * px

	ptrial = trial
		
plt.suptitle(argv[1])
plt.show()

# write to file
fo = open(argv[1] + '.trials', 'w')
for trial in trials:
	fo.write('%d %d\n' % (trial[0] * 512, trial[1] * 512))
