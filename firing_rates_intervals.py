#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 4:
	print 'USAGE: (1)<clu/res base> (2)<interval timestamps> (3)<output path>'
        print 'CALCULATE FIRING RATE IN GIVEN INTERVALS (CURRENTLY READING TIMETAMPS OF 100MS INTERVAL STARTS)'
	exit(0)

argv = resolve_vars(argv)

BASE = argv[1]
OUTPATH = argv[3]
istarts = np.loadtxt(argv[2])
clu = np.loadtxt(BASE + 'clu', dtype=np.int)
res = np.loadtxt(BASE + 'res', dtype=np.int)

intervals = [[st, st+2400] for st in istarts]

ires = 0
# NEXT OR CURRENT INTERVAL
ii = 0

scounts = [0] * (np.max(clu) + 1)

INSIDE = True

while ii < len(intervals):
    while ires < len(res) and res[ires] < intervals[ii][0]:
        if not INSIDE:
            scounts[clu[ires]] += 1
        ires += 1

    while ires < len(res) and res[ires] < intervals[ii][1]:
        if INSIDE:
            scounts[clu[ires]] += 1
        ires += 1

    ii += 1

#dursec = (res[-1] - (np.sum([ ii[1] - ii[0] for ii in intervals]))) / 24000.0
dursec = (np.sum([ ii[1] - ii[0] for ii in intervals])) / 24000.0

rates = np.array(scounts) / dursec

np.savetxt(OUTPATH, rates)
