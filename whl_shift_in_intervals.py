#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats

if len(argv) < 4:
	print('USAGE: (1)<whl file> (2)<intervals to shift at> (3)<shift value>')
	exit(0)

#whl = np.loadtxt(argv[1], dtype=int)
#ints = np.loadtxt(argv[2], dtype=int)
whl = np.loadtxt(argv[1], dtype=float)
ints = np.loadtxt(argv[2], dtype=float)

shift = int(argv[3])

iint = 0
iwhl = 0

if np.ndim(ints) == 1:
    ints = np.asmatrix(ints)

print(ints, len(ints))
print(ints[iint,0], ints[iint,1])

while iint < len(ints):
	while iwhl < len(whl) and whl[iwhl,-2] < ints[iint, 0]:
		iwhl += 1

	while iwhl < len(whl) and whl[iwhl,-2] < ints[iint, 1]:
		if whl[iwhl,0] < 1000:
			whl[iwhl,0] += shift
		if whl[iwhl,2] < 1000:
			whl[iwhl,2] += shift

		iwhl += 1

	iint += 1

np.savetxt(argv[1] + '.shift', whl, fmt='%d')
