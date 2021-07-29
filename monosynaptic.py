#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

# build cross-correlogram of cells i and j
# 	nw in both directions, win = windows size

def lag_hist(i, j, win, nw):
	ti = res[clu == i]
	tj = res[clu == j]

	i = 0
	j = 0
	
	while ti[i] < win * nw:
		i += 1
	cc = [0] * nw * 2	

	while i < len(ti) and j < len(tj) - 1:
		# find the first before (the next one is after then)
		while j < len(tj) - 1 and tj[j+1] < ti[i]:
			j += 1
		
		if j >= len(tj) - 1:
			break

		b = (tj[j] - ti[i]) / win + nw
		if b >= 0 and b < nw *2:
			cc[b] += 1
		
		b = (tj[j+1] - ti[i]) / win + nw
		if b < nw * 2:
			cc[b] += 1	

		i += 1

	return cc

def cross_corr(i, j, win, nw):
	ti = res[clu == i]
	tj = res[clu == j]

	i = 0
	j = 0
	
	while ti[i] < win * nw:
		i += 1

	cc = [0] * nw * 2

	start_j = 0
	while i < len(ti) and j < len(tj):
		# find new start
		while start_j < len(tj) and tj[start_j] < ti[i] - win * nw:
			start_j += 1

		# start from new start
		j = start_j
		while j < len(tj) and tj[j] < ti[i] + win * nw:
			b = (tj[j] - ti[i]) / win + nw
			cc[b] += 1
			j += 1
		
		i += 1

	return cc

if len(argv) < 4:
	print 'USAGE: (1)<clu/res base> (2)<FR threshold> (3)<monosyn factor>'
	exit(0)

BASE = argv[1]
MINR = float(argv[2])
MFAC = float(argv[3])

clu = read_int_list(BASE + 'clu')
res = read_int_list(BASE + 'res')

# calculate firing rates

CLUN = max(clu)

rates = []
DURSEC = res[-1] / 24000.0
for i in range(CLUN+1):
	rates.append(clu.count(i) / DURSEC)

print rates

rates = np.array(rates)
print np.where(rates > MINR), rates[rates > MINR]


clu = np.array(clu)
res = np.array(res)

NWIN = 30

for c in range(2, CLUN + 1):
	if rates[c] < MINR:
		continue

	ccs = []
	labs = []
	for c1 in range(2, CLUN + 1):
		if c1 == c:
			continue

		#if rates[c1] > MINR:
		#	continue

		# filter out candidates : peak in 5 ms around middle is at least 1.5X peak outside
		# cc = cross_corr(c, c1, 24, NWIN)
		cc = lag_hist(c, c1, 24, NWIN)

		max_in = max(cc[NWIN-5:NWIN+5])
		max_out = max(cc[:NWIN-5] + cc[NWIN+5:])
		if max_in >= MFAC * max_out and sum(cc) > 20:
			ccs.append(cc)
			labs.append('%d - %d' % (c, c1))

	NR = 6
	NC = 4
	for b in range(len(ccs) / (NR*NC) + 1):
		if len(ccs)  == 0:
			break

		fig, axarr = plt.subplots(NR, NC, figsize = (20, 16))

		k = 0
		for cc in ccs[b*NR*NC:min(len(ccs), (b+1)*NR*NC)]:
			ax = axarr[k % NR, k / NR]
			ax.bar(range(len(cc)), cc)
			ax.axvline(NWIN, color = 'r')
			ax.set_title(labs[k + b*NR*NC])
			
			k += 1
		plt.show()
