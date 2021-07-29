#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
#from call_log import *
from scipy import stats
from iutils_p3 import ztest

if len(argv) < 3:
	print('USAGE: (1)<within> (2)<between> (3)<animal ids>')
	exit(0)

abtw = np.loadtxt(argv[1])
awth = np.loadtxt(argv[2])
#an = np.array([s[:5] for s in open(argv[3]).readlines()])
an = np.array(open(argv[3]).read().splitlines())
anu = list(set(list(an)))

for a in anu:
    btw = abtw[an != a]
    wth = awth[an != a]

    nbtw = len(btw)
    nwth = len(wth)
    rbtw = np.corrcoef(btw[:,0], btw[:,1])[0, 1]
    rwth = np.corrcoef(wth[:,0], wth[:,1])[0, 1]

    print(a, ztest(rbtw, rwth, nbtw, nwth))
