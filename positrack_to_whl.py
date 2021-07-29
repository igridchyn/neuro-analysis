#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats

if len(argv) < 3:
	print('USAGE: (1)<positrack file> (2)<delay in sync sampling>')
	exit(0)

delay = int(argv[2])

posi = np.loadtxt(argv[1], skiprows=1)

# every 400 samples : 50 Hz at 20kHz dat file
# 9,10,12,13 : x/y; 1 or 2: sample (x20)
# 4 = -1.00 => unknown

pos_t1 = posi[0,1]

print('Unknown pos: %.2f %%' % (np.sum(posi[:,4] < 0) / len(posi) * 100))

for c in [9, 10, 12, 13]:
    posi[posi[:,4] < 0, c] = 1023

whl = np.hstack((posi[:,np.array([9, 10, 12, 13])], ((posi[:,1] - pos_t1) * 20 + delay).reshape(-1,1), (posi[:, 9] != 1023).astype(int).reshape(-1, 1)))

np.savetxt(argv[1].replace('positrack', 'whl'), whl, fmt='%.2f')
