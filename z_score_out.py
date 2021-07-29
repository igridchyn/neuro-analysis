#!/usr/bin/env python

# z-sciring outside of given intervals
# only full windows outside of given intervals are considered

from sys import argv
import numpy as np
from iutils import *

if len(argv) < 5:
	print 'USAGE: (1)<base path> (2)<timestamps> (3)<time window(ms)> (4)<output file>'
	exit(0)

argv = resolve_vars(argv)

base = argv[1]
tw = int(argv[3]) * 24

clu = [int(c)-1 for c in open(base + 'clu')]
res = [int(r) for r in open(base + 'res')]
NC = max(clu) + 1

# [beg mid end]
timestamps = []
for line in open(argv[2]):
	timestamps.append([int(t) for t in line.split(' ')])

# pop vecs
pvs = []

# index of the next timestamps to consider
ti = 0
ri = 0
pv = [0] * NC

# start of window
t = res[0]

pvi = 0
# max size ...
pvs = np.zeros((res[-1] / tw, NC))

while ri < len(res):
	pv[clu[ri]] += 1

	if res[ri] >= t + tw:
		# crossed the next interval
		if ti < len(timestamps) and res[ri] > timestamps[ti][0]:
			while ri < len(res) and res[ri] < timestamps[ti][2]:
				ri += 1
			ti += 1

			# adjust t as well and roll back one spike
			if ri < len(res):
				t = res[ri]
				ri -= 1			

			# assume intervals don't overlap!
		else:
			#pvs.append([(s*24000.0)/tw for s in pv])
			pvs[pvi, :] = [(s * 24000.0) / tw for s in pv]
			pvi += 1
			t += tw

		pv = [0] * NC

	ri += 1

print 'Collected %d population vectors' % len(pvs)

# pvs = np.array(pvs)
pvs = pvs[:pvi,:]

print pvs.shape

fout = open(argv[4], 'w')
for c in range(NC):
	# DEBUG
	#plt.hist(pvs[:,c])
	plt.hist(pvs[:,c] / 20, bins = 10, range = [0,10])
	plt.show()

	cellratesmean = np.mean(pvs[:,c])
	cellratesstd  =  np.std(pvs[:,c])
	fout.write('%f %f\n' % (cellratesmean, cellratesstd))
