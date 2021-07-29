#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

if len(argv) < 4:
	print 'USAGE: (1)<base name for pfs> (2)<session1> (3)<session2>'
	exit(0)

log_call(argv)

base = argv[1]
s1 = argv[2]
s2 = argv[3]

c = 1

pfs1 = []
pfs2 = []

MINR = 0.0
MAXR = 100
ind1, ind2 = cell_filter('../..', 'PFS_2_3_FTS_1_MEANS.out', 0.5, 0.3, '0', 0, MINR, MAXR)

nextpath = '%s%d_%s.mat' % (base, c, s1)
print nextpath
while os.path.isfile(nextpath):
	pf1 = np.loadtxt('%s%d_%s.mat' % (base, c, s1))
	pf2 = np.loadtxt('%s%d_%s.mat' % (base, c, s2))

	# norm by mean rates ? / peak rates ?
	pf1[np.isinf(pf1)] = np.nan
	pf2[np.isinf(pf2)] = np.nan
	pfm1 = np.nanmean(pf1)
	pfm2 = np.nanmean(pf2)
	pfma1 = np.nanmax(pf1)
	pfma2 = np.nanmax(pf2)
	print pfm1, pfm2
	
	# FILTER BY MEAN/MAX RATE
	#MINR = 0.5 / 50.0
	#if pfm1 > 0.00001 and pfm2 > 0.00001:
	#if pfm1 > MINR:
	#if pfm1 > MINR and pfm2 > MINR:
		# DOF : mean or max
	if pfm1 > 0.00001 and pfm2 > 0.00001:
		pf1 /= pfm1
		pf2 /= pfm2
	pfs1.append(pf1)
	pfs2.append(pf2)

	c += 1
	nextpath = '%s%d_%s.mat' % (base, c, s1)

# compare as population vectors
corrmap = np.zeros(pfs1[0].shape)

pfs1 = np.array(pfs1)
pfs2 = np.array(pfs2)

print 'Mat shape:', pfs1[0].shape

for yb in range(pfs1[0].shape[0]):
	for xb in range(pfs1[0].shape[1]):
		# DOF : filter or not
		ind = ind1 if xb < pfs1[0].shape[1] / 2 else ind2
		v1 = [pf[yb,xb] for pf in pfs1[ind]]
		v2 = [pf[yb,xb] for pf in pfs2[ind]]

		corrmap[yb, xb] = np.ma.corrcoef(v1, v2)[0, 1]

plt.imshow(corrmap, interpolation = 'none', clim=(0.0, 1.0))
#plt.imshow(corrmap, interpolation = 'none', clim=(0.7, 1.0))
#plt.colorbar(orientation = 'horizontal')
plt.tight_layout()
plt.show()
