#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 2:
	print 'USAGE: (1)<file with list of sleepcat files>'
        print 'PLOT DAYWISE SPLIT BARS WITH SLEEP CATEGORIES SPLIT'
	exit(0)

overall = []
for line in open(argv[1]):
    ar = np.loadtxt(line.strip())
    overall.append(ar)

overall = np.array(overall)

ind = range(11)
plt.bar(ind, overall[:,0])
for i in range(1, 3):
    plt.bar(ind, overall[:,i], bottom = np.sum(overall[:,:i], axis=1))

plt.legend(['REM', 'AWAKE', 'SLOW'], fontsize=15)
plt.show()
