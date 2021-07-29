#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
from tracking_processing import whl_to_pos
from call_log import log_call

if len(argv) < 10:
	print 'Cluster environment into bins wrt closest arm'
	print 'Usage: (1)<list of goal coordinates> (2)<nbins x> (3)<n binsy> (4)<bin size> (5)<whl [for validation] or -> (6)<center x of -1> (7)<center y or -1> (8)<radius center> (9)<output map file name>'
	exit(0)

#logdir = log_call(argv)

nbinsx = int(argv[2])
nbinsy = int(argv[3])
BIN = float(argv[4])

centx = float(argv[6])
centy = float(argv[7])
centrad = float(argv[8]) ** 2

whl = []
if argv[5] != '-':
	whl = whl_to_pos(open(argv[5]), False)

goals = []
for line in open(argv[1]):
	if len(line) == 0:
		continue

	ws = line.split(' ')
	goals.append([float(ws[0]), float(ws[1])])

print 'Goals: ', goals

mp = np.zeros((nbinsx, nbinsy))

for x in range(0, nbinsx):
	for y in range(0, nbinsy):
		cbx = (x + 0.5) * BIN
		cby = (y + 0.5) * BIN
		goalbest = 0
		distbest = (cbx - goals[0][0]) ** 2 + (cby - goals[0][1]) ** 2

		for gi in range(1, len(goals)):
			distgoal = (cbx - goals[gi][0]) ** 2 + (cby - goals[gi][1]) ** 2
			if distgoal < distbest:
				distbest = distgoal
				goalbest = gi

		if centx > 0:
			distcent = (cbx - centx) ** 2 + (cby - centy) ** 2
			if distcent < centrad:
				goalbest = len(goals)

		mp[x, y] = goalbest

np.savetxt(argv[9], mp)
#np.savetxt(logdir + 'sectors.gmap', mp)
fig = plt.figure()
plt.imshow(mp, interpolation = 'none')
#plt.savefig(logdir + 'sectors.png')

# sub-sample whl:
if len(whl) > 5000:
	s = len(whl) / 5000
	whl = [whl[i*s] for i in range(0, len(whl)/s)]

if len(whl) > 0:
	plt.scatter([w[1]/BIN for w in whl], [w[0]/BIN for w in whl])

plt.show()
