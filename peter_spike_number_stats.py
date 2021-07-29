#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os

if len(argv) < 3:
	print 'USAGE: (1)<base for clu / res / des> (2)<time window (ms)>'
	exit(0)

base = argv[1]
clu = np.loadtxt(base + 'clu', dtype = int)
clu = clu[1:]
res = np.loadtxt(base + 'res', dtype = int)
des = np.loadtxt(base + 'des', dtype = str)
despyr = des == 'p1'
twin = int(argv[2]) * 24

print 'Loaded clu / res / des ...'

# calculate mean and median number of spikes (pyramidals only and all) in given time window
t = -twin
nspyr = []
nsall = []
i = 0

while i < len(clu):
    t += twin
    nall = 0
    npyr = 0

    while i < len(res) and res[i] < t + twin:
        nall += 1
        npyr += int(despyr[clu[i] - 2])
        i += 1
    
    nspyr.append(npyr)
    nsall.append(nall)

print 'All cell spikes, median / mean: %d / %.2f' % (np.median(nsall), np.mean(nsall))
print 'Pyr cell spikes, median / mean: %d / %.2f' % (np.median(nspyr), np.mean(nspyr))
