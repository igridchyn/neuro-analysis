#!/usr/bin/env python

from sys import argv
import numpy as np

if len(argv) < 3:
	v1 = [float(v) for v in open(argv[1])]
	v2 = [float(v) for v in open(argv[2])]

	if len(v1) != len(v2):
		print 'ERROR: different data size'
		exit(1)

	print np.corrcoef(v1, v2)[0, 1]

else:
#matrix
	m1 = np.loadtxt(argv[1])
	m2 = np.loadtxt(argv[2])

	if m1.shape != m2.shape:
		print 'ERROR: different data size'
		exit(2)
	

	m1 = m1.flatten()
	m2 = m2.flatten()
	ind = ~np.isnan(m2) & ~np.isnan(m1) # & (np.abs(m1) > 0.00001) & (np.abs(m2) > 0.00001)
	m1 = m1[ind]
	m2 = m2[ind]

	print np.corrcoef(m1, m2)[0, 1]
	
