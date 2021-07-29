#!/usr/bin/env python

from sys import argv
from math import log
import numpy as np
from matplotlib import pyplot as plt
from iutils import *

def kern(val, s):
	return 1.0 / (s * np.sqrt(2 * np.pi)) * np.exp(- (val/float(s)) ** 2 / 2 )

NARG = 3
if len(argv) < NARG:
	print 'USAGE: (1)<timestamps> (2)<clu/res base> (3)<PFS file - for specificity>'
	print 'Plot session-wise mean firing rate around given timestamps versus realtive time and cell specificity'
	exit(0)

argv = resolve_vars(argv)

tspath = argv[1]
base = argv[2]
pfspath = argv[3]

# specificity: from pfs files

# timestamps - file

# frs: clu/rs

timestamps = [int(t) for t in open(tspath)]
clu = [int(c) for c in open(base + 'clu')]
res = [int(c) for c in open(base + 'res')]
NCELL = max(clu)

specificity = []
pfrs = []
fpfs = open(pfspath)

for line in fpfs:
	ws = line.split(' ')
	fr1 = float(ws[3])
	fr2 = float(ws[4])
	spec = 10 if fr2 == 0 else (-10 if fr1 == 0 else log(fr1/fr2))
	specificity.append(spec)
	pfrs.append(max(fr1, fr2))

# time bin number and width
NTBIN = 100
WTBIN = 24

# read sparsities / coherences
sp1 = read_float_array('../sparsity_BS6_OT5_E1.txt')
sp2 = read_float_array('../sparsity_BS6_OT5_E2.txt')
coh1 = read_float_array('../coherence_BS6_OT5_E1.txt')
coh2 = read_float_array('../coherence_BS6_OT5_E2.txt')

MAXSP = 0.3
MINCOH = 0.5
ind_spcoh = ((sp1 < MAXSP) & (coh1 > MINCOH)) | ((sp2 < MAXSP) & (coh2 > MINCOH))

# KDE of firing rates aroung events

st = 3 * 24 # 5 ms time kernel width
# pre-compute kernel
krn = []
for dt in range(NTBIN * WTBIN):
	krn.append(kern(dt, st))
print 'Done KRN'

# rates array
crates = np.zeros((NCELL + 1, NTBIN))

print 'WARNING: 1st half of sleep used'

ires = 0
for t in timestamps:
	while ires < len(res) and res[ires] < t - NTBIN/2 * WTBIN:
		ires += 1

	while ires < len(res) and res[ires] < t + NTBIN/2 * WTBIN:
		for tb in range(NTBIN):
			# crates[clu[ires]-1, tb] += kern(res[ires] - t - (tb - NTBIN/2) * WTBIN, st)
			crates[clu[ires]-1, tb] += krn[abs(res[ires] - t - (tb - NTBIN/2) * WTBIN)]
		ires += 1

	# ??? 1st half of sleep / first hour (172800000) / 30 minutes (86400000)
	if res[ires] > 172800000:
		break

# plot, ordered by selectivity along the y axis
sord = np.argsort(specificity)

# !!! normalized / standardized firing rates ?
#crates = crates / np.max(crates)

# FILTER
pfrs = np.array(pfrs)
MINPFR = 0.5
ind = (pfrs > MINPFR) & ind_spcoh 
# ind = ind_spcoh

# normalize by sleep-wise averages
for c in range(1, NCELL+1):
	crates[c-1,:] /= clu.count(c)

# ? normalize by time bin-wise averages ? of only valid ! cells !
#for t in range(1, NTBIN):
#	crates[:,t] /= np.nanmean(crates[sord[ind[sord]], t])

plt.imshow(crates[sord[ind[sord]], :NTBIN/2], interpolation = 'none', origin = 'lower')
plt.xlabel('Time')
plt.ylabel('Selectivity')
xt = range(0, NTBIN/2, NTBIN/2/5)
plt.xticks(xt, [str((t-NTBIN/2)*WTBIN/24) for t in xt])
plt.yticks([],[])
plt.show()
#for i in range(len(sord)):
#	plt.plot(crates[sord[i], :] + i)
#plt.show()
