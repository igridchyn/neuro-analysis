#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats

if len(argv) < 1:
	print('USAGE: (1)<> (2)<> (3)<>')
	exit(0)

d = [0.8642116, 0.81079, 0.91763, 0.8493898, 0.79063, 0.90813, 0.8617351, 0.80741, 0.91605]
d = np.array(d)

plt.bar([0, 1, 2], d[::3], color='darkblue')
plt.errorbar([0, 1, 2], d[::3], yerr=d[2::3]-d[::3],fmt='.', color='black')
plt.show()
