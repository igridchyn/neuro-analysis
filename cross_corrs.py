#!/usr/bin/env python2

from sys import argv
from matplotlib import pyplot as plt
from collections import Counter

# draw cross-correlogramms of high FR cells vs. rest

clu = []
res = []

if len(argv) < 2:
	print 'USAGE: (1)<session base 1 (ending with .)> ...(N)<session base N>'
	print 'Calculate cross-correlogramms of interneurons with other cells'

shift = 0
for base in argv[1:]:
	fclu = open(base + 'clu')
	fres = open(base + 'res')
	
	for line in fclu:
		if len(line) == 0:
			break

		clu.append(int(line))
		res.append(int(fres.readline()) + shift)

	shift = res[-1]

print str(len(res)) + ' spikes loaded'

nclu = max(clu)

occs = Counter(clu)

print occs

timesec = res[-1] / 24000.0

FRTHOLD = 7
ints = []
for k in occs:
	fr = occs[k] / timesec
	print 'cell %d, FR = %.2f spiks/sec' % (k, fr)
	if fr > FRTHOLD:
		ints.append(k)

# crete reverse index array
rev = [1000000] * (nclu + 1)
rmax = 0
for i in ints:
	rev[i] = rmax
	rmax += 1

# calculate cross-correlogramms

BIN = 6
NBIN = 80
ccs = []
for i in range(len(ints)):
	ccs.append([])
	for c in range(nclu + 1):
		ccs[i].append([0] * NBIN)
		

ri = 0
while ri < len(res):
	while ri < len(res) and clu[ri] not in ints:
		ri += 1

	# now check window around this spike and fill cc-s
	# find left edge first
	rc = ri
	while rc > 0 and res[ri] - res[rc] < NBIN * BIN / 2:
		rc -= 1
	rc += 1

	while rc < len(res) and res[rc] - res[ri] < NBIN * BIN / 2:
		bn = (res[rc] - res[ri]) / BIN + NBIN / 2
		# print bn, rev[clu[ri]], clu[rc]
		ccs[rev[clu[ri]]][clu[rc]][bn] += 1
		rc += 1

	ri += 1

print 'WARNING: HACKED TO CALCULATE ONLY INTS AUTO!'

# draw cc-s
nplot = 0
PMAX = 20
f, axarr = plt.subplots(5, 4, figsize=(20, 16), sharex = False, sharey = False)
for i in ints:
	#for c in range(nclu + 1):
        for c in ints:
		if nplot == PMAX:
			plt.show()
			f, axarr = plt.subplots(5, 4, figsize=(20, 16), sharex = False, sharey = False)
			nplot = 0

		axarr[nplot % 5, nplot / 5].bar(range(NBIN), ccs[rev[i]][c])
		axarr[nplot % 5, nplot / 5].set_title('IN: %d, C: %d' % (i, c))
		nplot += 1

plt.show()
