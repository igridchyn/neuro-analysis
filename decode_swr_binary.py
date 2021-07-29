#!/usr/bin/env python

import os
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from iutils import *
from scipy.stats import ttest_rel, ttest_ind, wilcoxon
from math import sqrt, log, exp
from tracking_processing import *

def decode(popv):
	lp1 = 0
	lp2 = 0
	lps = np.zeros((1, NBINS))
	# print nsliks.shape
	for c in range(min(NCELL, nsliks.shape[1])):
		if not FRATES or ifrates[c]:
			#lp1 += e1logps[c][min(popv[c], MAXN)]
			#lp2 += e2logps[c][min(popv[c], MAXN)]
			if NBINS == 2:
				lp1 += nsliks[0,c,min(popv[c], MAXN)]
				lp2 += nsliks[1,c,min(popv[c], MAXN)]
			else:
				# print nsliks[:, c, min(popv[c], MAXN)].shape
				lps += nsliks[:, c, min(popv[c], MAXN)]

	lps = np.transpose(lps)
	if NBINS == 2:
		return lp1, lp2, 0, 0, np.log(np.exp(lp1)+np.exp(lp2))
	else:
		# lps[np.isinf(lps)] = np.nan
		# print lps.transpose()
		return np.nanmax(lps[:NBINS/2]), np.nanmax(lps[NBINS/2:]), np.log(np.nanmean(np.exp(lps[:NBINS/2]))), np.log(np.nanmean(np.exp(lps[NBINS/2:]))), np.log(np.nanmean(np.exp(lps)))

def zerif(a):
	return 0 if NBINS == 2 else a

if len(argv) < 6:
	print 'USAGE: (1)<basename> (2)<model file - log likelihoods of e1 for cell/spike#> (3)<swr file> (4)<number of spikes> (5)<output file> (6)<firing rates>'
	exit(0)

set_print_format()

# psopt
#NBINS = 100
#print 'WARNING: NBINS = 100'

argv = resolve_vars(argv)

base = argv[1]
mpath = argv[2]
swrpath = argv[3]
spiken = int(round(float(argv[4])))
foutpath = argv[5]

FRATES = False
if len(argv) > 6:
	FRATES = True
	fratespath = argv[6]
	frates = [float(f) for f in open(fratespath)]

	MAXRATE = 100
	print 'WARNING: cells with max rates %d considered' % MAXRATE
	ifrates = (np.array(frates) < MAXRATE) & (np.array(frates) > 0.5)
	print '%d cells out of %d pass the FR filter ' % (np.sum(ifrates), len(ifrates))

clu = [int(c)-1 for c in open(base + 'clu')]
res = [int(c) for c in open(base + 'res')]
# full swr entry: start peak end
FULL = True
print 'WARNING: hard-coded FULL swr mode'
if FULL:
	swrs = [[int(w) for w in s.split(' ')] for s in open(swrpath)]
else:
	swrs = [int(s) for s in open(swrpath)]

NCELL = max(clu) + 1

#e1logps = np.load(mpath)
#nsliks = np.load(mpath.replace('npy', 's.npy'))
# 2nd - non-Poisson model, 3rd - Poisson model
(e1logps, dummy, nsliks) = np.load(mpath)
NBINS = nsliks.shape[0]
print 'NSLIKS shape:', nsliks.shape
e2logps = np.log(1-np.exp(e1logps))
MAXN = nsliks.shape[2] - 1

fout = open(foutpath, 'w')

ires = 0
for si in range(len(swrs)):
	# find first spike after
	if FULL:
		while ires < len(res) and res[ires] < swrs[si][0]:
			ires += 1
	else:
		tswr = swrs[si]
		while ires < len(res) and res[ires] < tswr:
			ires += 1

	if ires >= len(res):
		break

	# decode from previous spiken spikes
	sn = [0] * NCELL
	if FULL:
		while ires < len(res) and res[ires] < swrs[si][1]:
			sn[clu[ires]] += 1 
			ires += 1
	else:
		for ci in range(max(0, ires-spiken), ires):
			sn[clu[ci]] += 1
	lp1b, lp2b, lp1bs, lp2bs, sumb = decode(sn)

	# decode from next spiken spikes
	sn = [0] * NCELL
	if FULL:
		while ires < len(res) and res[ires] < swrs[si][2]:
			sn[clu[ires]] += 1 
			ires += 1
	else:
		for ci in range(ires, min(len(res)-1, ires + spiken)):
			sn[clu[ci]] += 1
	lp1a, lp2a, lp1as, lp2as, suma  = decode(sn)

	# write likelihoods in the file - simulate swrdec format
	# print lp1b, lp2b, lp1a, lp2a

	#sumb = np.log(np.exp(lp1b)+np.exp(lp2b)) if NBINS == 2 else np.log(np.exp(lp1bs) + np.exp(lp2bs))
	#suma = np.log(np.exp(lp1a)+np.exp(lp2a)) if NBINS == 2 else np.log(np.exp(lp1as) + np.exp(lp2as))

	if FULL:
		fout.write('%d %d %d %f %f %f %f 0 0 0 0 %f\n' % (si, swrs[si][0], swrs[si][1], lp1b, lp2b, lp1bs, lp2bs, sumb))
		fout.write('%d 0 0 0 0 0 0 0 0 0 0 0\n' % si) 
		fout.write('%d %d %d %f %f %f %f 0 0 0 0 %f\n' % (si, swrs[si][1], swrs[si][2], lp1a, lp2a, lp1as, lp2as, suma))
	else:
		fout.write('%d %d %d %f %f %f %f 0 0 0 0 %f\n' % (si, res[max(0, ires-spiken)], res[min(len(res)-1, ires+spiken)], lp1b, lp2b, lp1bs, lp2bs, sumb))
		fout.write('%d 0 0 0 0 0 0 0 0 0 0 0\n' % si) 
		fout.write('%d %d %d %f %f %f %f 0 0 0 0 %f\n' % (si, res[max(0, ires-spiken)], res[min(len(res)-1, ires+spiken)], lp1a, lp2a, lp1as, lp2as, suma))
