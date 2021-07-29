#!/usr/bin/env python

import glob
from numpy import genfromtxt
from matplotlib import pyplot as plt
from sys import argv
from numpy import exp

if len(argv) < 2:
	print 'Usage: ' + argv[0] + ' (1)<pattern of matrices to load (using wildcards)>'
	print 'Ouput: figure 1 - sum of 2 matrices'
	exit(0)

first = True
cnt = 0
for path in glob.glob(argv[1]):
	mat = genfromtxt(path)
	if first:
		sm = mat
		first = False
	else:
		sm += mat
	cnt += 1

sm /= cnt
plt.imshow(exp(sm.transpose()))
plt.colorbar()
plt.show()
