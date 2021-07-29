#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats

if len(argv) < 2:
	print('USAGE: (1)<session shifts file> (2)<merged whl path> (3-N)<whl files>')
	exit(0)

ses_sh = np.loadtxt(argv[1])
ises = -1

for whlpath in argv[3:]:
    whl = np.loadtxt(whlpath)
    if ises >= 0:
        whl[:,4] += ses_sh[ises]
        mwhl = np.vstack((mwhl, whl))
    else:
        mwhl = whl

    ises += 1

unkind = mwhl[:,5] < 0.5

# subtract min
for col in [0,1,2,3]:
    mwhl[:, col] -= np.min(mwhl[:,col]) - 5
    mwhl[unkind, col] = 1023


np.savetxt(argv[2], mwhl, fmt = '%.2f '*4 + '%d '*2)
