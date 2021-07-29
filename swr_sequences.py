#!/usr/bin/env python

from matplotlib import pyplot as plt
from sys import argv
from numpy import mean, std
from tracking_processing import whl_to_pos
from call_log import *
import numpy as np

def next_arm(timestart, mp):
	# assumes global whl
	maxarm = np.max(mp)
	occ = [0] * (maxarm + 1)

	# number of tracking points withing a region to trigger a visit
	VISTHOLD = 100
	MAXDUR = 10000
	visit = -1
	for t in range(timestart, min(len(whl), timestart + MAXDUR)):
		xbt = int(round(whl[t][0] / BIN))
		ybt = int(round(whl[t][1] / BIN))
		# print xbt, ybt
		if xbt > 0.01:
			# TODO : ORDER?
			maparm = int(mp[xbt, ybt])
			occ[maparm] += 1
			if occ[maparm] >= VISTHOLD:
				visit = maparm
				break

	return visit 	

#=================================================================================================================

if len(argv) < 7:
	print 'Usage: (1)<HMM - decoding dump file (swrdec)> (2)<likelihood threshold> (3)<dim (1/2)> (4)<whl file or - > (5)<bin size> (6)<path to regions map or ->'
	exit(0)

logdir=log_call(argv)

f = open(argv[1])
LTHOLD = float(argv[2])

seqs = []
liks = []
stime = []

dim = int(argv[3])
BIN = int(argv[5])

whlpath = argv[4]
mappath = argv[6]
havew = (whlpath != '-')
havem = (mappath != '-')

if havew:
	whl = whl_to_pos(open(whlpath), False)

if havem:
	mp = np.loadtxt(mappath)

l = f.readline()
while l:
	ws = l.split(' ')
	if len(ws) == 0:
		l = f.readline()
		continue

	n = int(ws[-1])
	liks.append(float(ws[2]))
	stime.append(int(ws[1]))

	seq = []
	for i in range(0, n):
		nl = f.readline()
		coords = [int(c) for c in nl.split(' ')]
		if dim == 1:
			seq.append([i, coords[0]])
		else:
			seq.append([coords[0], coords[1]])

	seqs.append(seq)
	l = f.readline()

	#if len(seqs) > 500:
	#	break

print 'read %d sequences' % len(seqs)
print 'Likelihoods mean / standard deviation: %.2f / %.2f' % (mean(liks), std(liks))

fig = plt.figure()
plt.hist(liks)
plt.show()
fig.savefig(logdir + 'SEQ_LIKS_HIST.png')

# quantify trajectory smoothness - distribution of distances between neighbouring bins / variance of (traj[t+1] - traj[t])
trajvars = []
si = -1
for seq in seqs:
	tdiffs = []
	si += 1
	if dim == 1:
		# OPTIONAL
		if liks[si] < LTHOLD:
			continue

		for i in range(1, len(seq)):
			tdiffs.append(seq[i][1] - seq[i-1][1])
		trajvars.append(std(tdiffs))

if dim == 2:
	print '2D trajectories variance not analuzed'		

print 'Speed standard deviation OF TRAJ > THOLD mean/std: %.2f / %.2f' % (mean(trajvars), std(trajvars))

nplot = 1
s = 0
while s < len(seqs):
	rlim = min(s + nplot, len(seqs))
	haveEvents = False
	for i in range(s, rlim):
		if liks[i] < LTHOLD:
			continue

		fig = plt.figure(figsize = (16, 12))
		haveEvents= True
		seq = seqs[i]
		xs = [se[0] for se in seq]
		# ys = [se[1] + 186*i for se in seq]
		ys = [se[1] for se in seq]

		pl = plt.plot(xs, ys, linewidth = liks[i] / 500 + 1,	alpha=0.5)
		lastcol = pl[0].get_color()

		# plot position of an event if available
		if havew:
			whls = whl[stime[i] / 480]
			if whls[0] > 0:
				plt.scatter([whls[0] / BIN], [whls[1] / BIN], s=80, color = lastcol, marker='^', alpha = 0.75)

	if not haveEvents:
		s += nplot
		continue
		print 'Skip event'

	# plot position at the time of the sequence
	if havew:
		whli1 = stime[s] / 480
		whli2 = stime[rlim-1] / 480
		subw = whl[whli1:whli2]
		plt.scatter([p[0] / BIN for p in subw if p[0] > 0], [p[1] / BIN for p in subw if p[0] > 0], color='black', s=0.5)

		# plot NEXT POSITIONS ! - next 15 sec
		wstart = whli1
		whli1 = whli2
		whli2 = min(len(whl)-1, whli2 + 15 * 50)
		subw = whl[whli1:whli2]
		plt.scatter([p[0] / BIN for p in subw if p[0] > 0], [p[1] / BIN for p in subw if p[0] > 0], color='red', s=0.5)

		plt.title(str(stime[s]) + ' - ' + str(stime[rlim-1]))

		# plot PREVIOUS positions - 15 sec	
		whli2 = wstart
		whli1 = max(0, whli2 - 15 * 50)
		subw = whl[whli1:whli2]
                plt.scatter([p[0] / BIN for p in subw if p[0] > 0], [p[1] / BIN for p in subw if p[0] > 0], color='green', s=0.5)

		# plot EARLIER PREVIOUS positions - 15 sec	
		whli2 = whli1
		whli1 = max(0, whli2 - 15 * 50)
		subw = whl[whli1:whli2]
                plt.scatter([p[0] / BIN for p in subw if p[0] > 0], [p[1] / BIN for p in subw if p[0] > 0], color='blue', s=0.5)

		# which arm is next / previous?
		if havem:
			nextarm = next_arm(stime[rlim-1] / 480, mp)
			print 'Next arm number: %d' % nextarm

	plt.show()
	fig.savefig(logdir + 'SEQS_' + str(s) + '.png')
	s += nplot	
	
	
