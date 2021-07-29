#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 2:
	print 'USAGE: (1)<base for clu/res>'
	exit(0)

argv = resolve_vars(argv)

base = argv[1]

clu = np.loadtxt(base + 'clu', dtype=int)
res = np.loadtxt(base + 'res', dtype=int)

ncell = max(clu) + 1
print 'Number of cells:', ncell

lasts = [0] * ncell
lastsa = [[] for i in range(ncell)]
maxint = 24*30

isis = [[] for i in range(ncell)]

for i in range(len(clu)):
    c = clu[i]

    while len(lastsa[c]) > 0 and res[i] - lastsa[c][0] > maxint:
        del lastsa[c][0]
    
#    if lasts[c] > 0:
#        isis[c].append(res[i] - lasts[c])
#        # to be suymmetric
#        isis[c].append(-(res[i] - lasts[c]))

    if len(lastsa[c]) > 0:
        for tc in lastsa[c]:
            isis[c].append(res[i] - tc)
            isis[c].append(tc - res[i])

    lasts[c] = res[i]

    lastsa[c].append(res[i])

# calc rates
frs = []
clu = list(clu)
for i in range(ncell):
    frs.append(clu.count(i) * 24000/ float(res[-1]))

print frs

MINR = 3
for i in range(ncell):
    if frs[i] > MINR:
        # print np.mean(isis[i])
        # print isis[i]
        bins = range(-30*24, 30*24, 24)
        plt.hist(isis[i], bins = bins)
        plt.title('CELL %d, %.1f hz' % (i, frs[i]))
        plt.show()
