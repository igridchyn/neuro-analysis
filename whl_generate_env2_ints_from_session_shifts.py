#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats

if len(argv) < 3:
	print('USAGE: (1)<session_shifts file> (2-N)<Numbers of sessions of environment 2, 1-based>')
	exit(0)

inds = np.array([int(s) for s in argv[2:]]) - 1 # 0-based
ss=np.loadtxt(argv[1], dtype=int)
ss=np.insert(ss,0,0)
ints = np.vstack((ss[inds], ss[inds+1]))
np.savetxt('env2_ints.txt', ints.transpose(), fmt='%d')
