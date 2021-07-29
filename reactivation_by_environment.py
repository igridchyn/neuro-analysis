#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
import numpy as np

if len(argv) < 4:
	print 'Usage: (1)<base session 1 - ending with .> (2)<base session 2 - ending with .> (3)<min firing rate>'
	print 'Compute co-firing correlations for 2 given sessions from correlation and firing rate (for filtering) files'
	exit(0)

base1 = argv[1]
base2 = argv[2] 
minfr = float(argv[3])

corre1s1 = np.loadtxt(base1 + 'corr_e1')
corre2s1 = np.loadtxt(base1 + 'corr_e2')
corre1s2 = np.loadtxt(base2 + 'corr_e1')
corre2s2 = np.loadtxt(base2 + 'corr_e2')

frse1s1 = np.loadtxt(base1 + 'frs_e1')
frse2s1 = np.loadtxt(base1 + 'frs_e2')
frse1s2 = np.loadtxt(base2 + 'frs_e1')
frse2s2 = np.loadtxt(base2 + 'frs_e2')

ncell = corre1s1.shape[0]

# make lists of correlation using firing rate threshold
lcorrs_e1_s1 = []
lcorrs_e2_s1 = []
lcorrs_e1_s2 = []
lcorrs_e2_s2 = []

for c1 in range(ncell):
	for c2 in range(c1):
		if frse1s1[c1] > minfr and frse1s2[c1] > minfr and frse1s1[c2] > minfr and frse1s2[c2] > minfr:
			lcorrs_e1_s1.append(corre1s1[c1, c2])
			lcorrs_e1_s2.append(corre1s2[c1, c2])

		
		if frse2s1[c1] > minfr and frse2s2[c1] > minfr and frse2s1[c2] > minfr and frse2s2[c2] > minfr:
			lcorrs_e2_s1.append(corre2s1[c1, c2])
			lcorrs_e2_s2.append(corre2s2[c1, c2])

reac_e1 = np.corrcoef(lcorrs_e1_s1, lcorrs_e1_s2)
reac_e2 = np.corrcoef(lcorrs_e2_s1, lcorrs_e2_s2)

# print reac_e1, reac_e2

print 'Environment-wise reactivations: %.2f / %.2f' % (reac_e1[0, 1], reac_e2[0, 1])
