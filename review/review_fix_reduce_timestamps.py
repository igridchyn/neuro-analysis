#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 2:
	print 'USAGE: (1)<input - swr timestamps>'
        print 'WORKAROUND FOR BUG CAUSED ADDITION OF 6M TO DETECTED SWR TIMESTAMPS'
	exit(0)

swrs = np.loadtxt(argv[1], dtype = int)

if swrs[0][0] < 6000000:
    print 'WARNING: too small value of first SWR timestamps to fix!'
    #exit(0)

swrs -= 6000000
#np.savetxt('tmpsw', swrs, fmt='%d')
np.savetxt(argv[1], swrs, fmt='%d')
