#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from tracking_processing import whl_to_pos, whl_to_speed
import matplotlib.animation as animation
from scipy import stats

def plot_kde(kernel):
	xmin=0
	ymin=0
	xmax=400
	ymax=200
	X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
	positions = np.vstack([X.ravel(), Y.ravel()])
	Z = np.reshape(kernel(positions).T, X.shape)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r, extent=[xmin, xmax, ymin, ymax])
	# ax.plot(m1, m2, 'k.', markersize=2)
	ax.set_xlim([xmin, xmax])
	ax.set_ylim([ymin, ymax])
	# plt.colorbar()
	plt.show()

if len(argv) < 3:
	print 'USAGE: (1)<base for whl, clu, res> (2)<speed threshold>'
	exit(0)

argv = resolve_vars(argv)

log_call(argv)

base = argv[1]
ST = float(argv[2])
EBORD = 180

whl = whl_to_pos(open(base + 'whl'), False)
speed = whl_to_speed(whl)

clu = read_int_list(base + 'clu')
res = read_int_list(base + 'res')

# for kde, speed-filtered
# whl_s = np.vstack([[whl[i][0] for i in range(len(whl)) if speed[i] > ST],[[whl[i][1] for i in range(len(whl)) if speed[i] > ST]]])


NCELL = max(clu)
coms1 = [] # cumulative coordinates for each cell [x, y]
coms2 = [] # cumulative coordinates for each cell [x, y]i
coms = [coms1, coms2]
ns1 = [0] * NCELL
ns2 = [0] * NCELL
ns = [ns1, ns2]
for c in range(NCELL):
	coms[0].append([0, 0])
	coms[1].append([0, 0])

intervals = []
# load intervals according to session: learning, post-probe, post-learning
pth = os.getcwd()
if 'post' in pth:
	intervals = [[0, 100000000]]
else:
	# read trials
	ftr = open(base + 'whl.trials')
	trials = []
	for line in ftr:
		trials.append([int(t) for t in line.split(' ')])
	
	if '9l' in pth:
		if '1123' in pth:
			intervals.append([0, trials[21][1]])
		else:
			# use first 10 trials
			intervals.append([0, trials[10][1]])
	elif '16l' in pth:
		intervals.append(trials[0])
		if '1123' in pth:
			intervals.append(trials[10])
		elif '1129' in pth:
			intervals.append(trials[3])
		elif '0106' in pth:
			intervals.append(trials[1])
		else:
			intervals.append(trials[5])	
	else:
		print 'ERROR: uknown session'
		exit(1)
	
print 'Intervals:', intervals
iind = 0

#plt.hist([s for s in speed if s < 10])
#plt.show()

whl_s = []
for i in range(len(whl)):
        t = i * 480
        sp = speed[i]

	if whl[i][0] < 0.01:
		continue

        if t > intervals[iind][1]:
                # go to next interval or exit if out of intervals 
                if iind == len(intervals) - 1:
                        break
                else:
                        iind += 1
                        while i < len(whl) and i*480 < intervals[iind][0]:
                                i += 1
                        continue

	if sp > ST:
		whl_s.append(whl[i])

whl_s = np.vstack([[w[0] for w in whl_s], [w[1] for w in whl_s]])
kernel = stats.gaussian_kde(whl_s)
# DEBUG plot pos kde
# plot_kde(kernel)

for i in range(len(clu)):
	c = clu[i] - 1
	t = res[i]
	twhl = res[i] / 480
	sp = speed[twhl]
	
	if t > intervals[iind][1]:
		# go to next interval or exit if out of intervals 
		if iind == len(intervals) - 1:
			break
		else:
			iind += 1
			while i < len(res) and res[i] < intervals[iind][0]:
				i += 1
			continue

	if sp > ST and whl[twhl][0] > 0.001:
		x = whl[twhl][0]
		e = int(x > EBORD)
		k = kernel([whl[twhl]])[0]
		if k > 1e-5:
			# INVERSE ?
			coms[e][c][0] += whl[twhl][0] / (k*100000)
			coms[e][c][1] += whl[twhl][1] / (k*100000)
			ns[e][c] += 1/(k*100000)

SC = 6.0
for c in range(NCELL):
	if ns[0][c] > 0:
		coms[0][c][0] /= float(ns[0][c]) * SC
		coms[0][c][1] /= float(ns[0][c]) * SC
	if ns[1][c] > 0:
		coms[1][c][0] /= float(ns[1][c]) * SC
		coms[1][c][1] /= float(ns[1][c]) * SC
		print 'Cell %d centers of mass' % c, coms[0][c], coms[1][c]
	else:
		print 'No spikes of cell', c

# write celter of mass

outpath = base + 'rev2.com'
if os.path.isfile(outpath):
	print 'The destination file exists:', base + 'com'
	exit(1)

if os.path.isfile(outpath):
	print 'ERROR: output file exists!'
	exit(1)

fo = open(outpath, 'w')
for c in range(NCELL):
	fo.write((4*'%.2f '+'\n') % (coms1[c][0], coms1[c][1], coms2[c][0], coms2[c][1]))	
