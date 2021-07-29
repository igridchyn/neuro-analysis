#!/usr/bin/env python

from sys import argv
import numpy as np
from iutils import *

if len(argv) < 8:
	print '(1)<values e1> (2)<values e2> (3)<firing rates s1> (4)<firing rates s2> (5)<firing rate threshold> (6)<responses> (7)<response threshold>'
	exit(0)

argv = resolve_vars(argv)

m1 = np.loadtxt(argv[1])
m2 = np.loadtxt(argv[2])

if m1.shape != m2.shape:
	print 'ERROR: different data size'
	exit(2)

frs_s1 = np.loadtxt(argv[3])
frs_s2 = np.loadtxt(argv[4])
frthold = float(argv[5])
responses = np.loadtxt(argv[6])
resp_thold = float(argv[7])

# print m1.shape

ind = (frs_s2 > frthold) & (frs_s1 > frthold) & (responses >h resp_thold) # & (frs_s2 < 15) & (frs_s1 < 15)

#if 'e1' in argv[1]:
#	frs_e2 = np.loadtxt(argv[3].replace('e1', 'e2'))
#	ind = ind & (frs_s1 > 2 * frs_e2)
#else:
#	frs_e1 = np.loadtxt(argv[3].replace('e2', 'e1'))
#	ind = ind & (frs_s1 > 2 * frs_e1)

# ind = (frs_s2 < frthold) & (frs_s1 < frthold) & (np.abs(responses) > resp_thold)

# print ind 
idx = np.array(range(len(ind)))[ind]
# print type(idx)

m1 = m1[idx, :]
m1 = m1[:, idx]
m2 = m2[:, idx]
m2 = m2[idx, :]

print m1.shape[0], ' cells'

#m1 = m1.flatten()
#m2 = m2.flatten()
#ind = ~np.isnan(m2) & ~np.isnan(m1) # & (np.abs(m1) > 0.00001) & (np.abs(m2) > 0.00001)
#m1 = m1[ind]
#m2 = m2[ind]

m1l = []
m2l = []
# form lists of correlations:
for i in range(m1.shape[0]):
	for j in range(i):
		if not np.isnan(m1[i, j]) and not np.isnan(m2[i,j]):
			m1l.append(m1[i,j])		
			m2l.append(m2[i,j])

#cc = np.corrcoef(m1, m2)[0, 1]

if len(m1l) > 0:
	cc = np.corrcoef(m1l, m2l)[0, 1]
	print cc

	foutcl = open(argv[3].split('.')[-1] + '.corlist', 'w')
	for i in range(len(m1l)):
		foutcl.write('%f %f\n' % (m1l[i], m2l[i]))

	fout = open(argv[3].split('.')[-1] + '.cofcorr', 'w')
	key = 'e1' if 'e1' in argv[3] else 'e2'
	fout.write(str(cc) + '\n')
else:
	print 'WARNING: NO CELLS, write empty list / nan correlation files'
	foutcl = open(argv[3].split('.')[-1] + '.corlist', 'w')
	fout = open(argv[3].split('.')[-1] + '.cofcorr', 'w')
	fout.write('nan\n')
	
