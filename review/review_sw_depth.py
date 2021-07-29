#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
import struct

if len(argv) < 6:
	print 'USAGE: (1)<dat file> (2)<channel> (3)<timestamps> (4)<window after timestamp for averaging, ms> (5)<output file - avg. depth every minute>'
        print 'CALCULATE AVERAGE ABSOLUTE LFP VALUE IN SMALL WINDOW GIVEN INTERVALS FOR GIVEN TIMESTAMPS'
	exit(0)

f = open(argv[1], 'rb')
chan = int(argv[2])
swt = np.loadtxt(argv[3], dtype=int)[:,1]
win = int(argv[4]) * 24
outpath = argv[5]
#o = open(argv[5], 'w')

swavgs = [0] * 120
swavgsc = [0] * 120
swrep = 200

for i in range(len(swt)):
    f.seek(128 * 2 * (swt[i]))

    winvals = []
    for w in range(win):
        nr = f.read(2 * chan)
        if len(nr) < 2 * chan:
            print 'EOF'
            break
        winvals.append(struct.unpack('h', f.read(2))[0])
        f.read(2 * (128-chan-1))
    
    minu = swt[i] / (24000 * 60)
    if minu < 120:
        #swavgs[minu] += np.mean(winvals)
        #swavgs[minu] += min(winvals)
        swavgs[minu] += max(winvals) - min(winvals)
        swavgsc[minu] += 1
    else:
        print 'MINU OOR:', minu
        break

    if (i+1) % swrep == 0:
        print i

swavgs = np.array(swavgs)
swavgsc = np.array(swavgsc)

swavgsc[swavgsc == 0] = 1

swavgs /= swavgsc

np.savetxt(outpath, swavgs)
