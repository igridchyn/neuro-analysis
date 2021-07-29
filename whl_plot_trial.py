#!/usr/bin/env python

from sys import argv
from math import sqrt, ceil
from tracking_processing import *
from matplotlib import pyplot as plt

if len(argv) < 3:
	print 'USAGE: (1)<whl file> (2)<trials file>'
	print 'PLOT TRAJECTORIES BY TRIAL'
	exit(0)

whl = whl_to_pos(open(argv[1]), True)
trials = []
for line in open(argv[2]):
	ws = line.split(' ')
	trials.append([int(ws[0]), int(ws[1])])

n = int(ceil(sqrt(len(trials))))
fig, axarr = plt.subplots(n, n)
for t in range(len(trials)):
	print trials[t][0]/480
	wtrial = whl[trials[t][0]/480 : trials[t][1]/480]
	axarr[t / n, t % n].plot([w[0] for w in wtrial], [w[1] for w in wtrial])
	axarr[t / n, t % n].set_title(str(t))
plt.show()
