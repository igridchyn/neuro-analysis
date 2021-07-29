#!/usr/bin/env python

from sys import argv
import numpy as np

if len(argv) < 3:
	print 'USAGE: (1)<basename of cluster files (clu/res)> (2)<z-score : 0/1>'
	print 'Generate Z-scores for firing rate and Z-scored firing rates'
	exit(0)

base = argv[1]
zscore = bool(int(argv[2]))

cluf = open(base + 'clu')
resf = open(base + 'res')

n = int(cluf.readline())
print str(n), ' cells'

clu = [int(c) for c in cluf if len(c) > 0]
res = [int(c) for c in resf if len(c) > 0]
print 'Number of spikes: ', len(clu)

w = 2000
maxt = res[-1] / w + 1

print 'Number of time windows: ', maxt

ifrs = []
for i in range(n + 1):
	ifrs.append([0] * maxt)

t = 0
ti = 0
resi = 0
ns = [0] * (n + 1)

while i < len(res):
	# number of spikes in the window

	# for all spikes in the current timewindow (t to t+w)
	while i < len(res) and res[i] < t + w:
		ns[clu[i]] += 1
		i += 1

	# assign current ifrs for ti-s window
	for c in xrange(n + 1):
		ifrs[c][ti] = ns[c]
		ns[c] = 0

	ti += 1
	t += w

if zscore:
	mns = []
	stds = []
	# calculate means and stds
	fo = open(base + 'z', 'w')
	for i in range(1, n + 1):
		print 'cell %d: %.2f / %.2f' % (i, np.mean(ifrs[i]), np.std(ifrs[i]))
		fo.write('%.2f %.2f\n' % (np.mean(ifrs[i]), np.std(ifrs[i])))
		mns.append(np.mean(ifrs[i]))
		stds.append(np.std(ifrs[i]))
	fo.close()

	# write z-scored firing rates per window
	fo = open(base + 'frz', 'w')
	for ti in range(maxt):
		for c in range(1, n + 1):
			fo.write(str((ifrs[c][ti] - mns[c-1]) / stds[c-1]) + ' ')
		fo.write('\n')
	fo.close()

else:
	# write z-scored firing rates per window
	fo = open(base + 'frz', 'w')
	for ti in range(maxt):
		for c in range(1, n + 1):
			fo.write(str(ifrs[c][ti]) + ' ')
		fo.write('\n')
	fo.close()
