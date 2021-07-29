#!/usr/bin/env python2

from numpy.polynomial.polynomial import polyfit
from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

if len(argv) < 4:
	print 'USAGE: (1)<dirs list> (2)<file name 1> (3)<file name 2>'
	exit(0)

fdirs = argv[1]
fname1 = argv[2]
fname2 = argv[3]
fnames = [fname1, fname2]

sm = []
convlen = 50 # 250 . 500
ndirs = 0

print 'WARNING: take THIRD OF VALUES ONLY !'

for line in open(fdirs):
    #print line
    if len(line) < 2:
            continue

    # READ WHICH ENV IS TARGET
    for aline in open(line[:-1] + '/../about.txt'):
        if aline.startswith('swap'):
            swap = bool(int(aline[-2]))
            #print swap
            break

    #vals = np.loadtxt(line[:-1] + '/' + fname)
    vals = np.loadtxt(line[:-1] + '/' + fnames[int(swap)])
    valsalt = np.loadtxt(line[:-1] + '/' + fnames[1 - int(swap)])

    print 'WARNING: MAX ELEMENTWISE OF THE TWO!'
    vals = np.maximum(vals, valsalt)

    if len(vals) == 0:
        print 'EMPTY AT line, CONTINUE'
        continue
    
    ndirs += 1

    # !!! 1st / last window of every SWR !!!
    #vals = vals[[3*i for i in range(len(vals)/3)]]
    vals = vals[[(3*i+2) for i in range(len(vals)/3-1)]]
    print len(vals)

    # FILTER - RATHER REPLACE !!!
    vals = vals[vals != 0]
    #vals = vals[~np.isinf(vals) & ~np.isnan(vals)]
    vals[np.isinf(vals)] = np.nan
    if np.isinf(vals[0]) or np.isnan(vals[0]):
        vals[0] = np.nanmean(vals)
    for i in range(1, len(vals)):
        if np.isinf(vals[i]) or np.isnan(vals[i]):
            vals[i] = vals[i-1]

    # TO GET PROB FROM LIKELIHOOD
    vals = np.exp(vals)

    # SMOOTH
    # vals = np.convolve(vals, [1.0/convlen] * convlen)[convlen:-convlen]

    # STANDARDIZE
    #vals = (vals - np.mean(vals)) / np.std(vals)

    if len(sm) == 0:
        sm = vals
    else:
        nlen = min(len(sm), len(vals))
        sm = sm[:nlen] + vals[:nlen]

    # sm /= len(vals)

sm /= ndirs

b,a = polyfit(range(len(sm)), sm, 1)

FSLAB = 25

plt.plot(sm, linewidth=4)
plt.plot([0, len(sm)], [b, b + a*len(sm)], color='black')
plt.xlabel('Sleep time, h', fontsize = FSLAB)
#plt.ylabel('Likelihood, Z-score', fontsize = FSLAB)
plt.ylabel('Max bin probability', fontsize = FSLAB)

plt.gca().locator_params(nbins=5, axis='y')
set_yticks_font(25)
plt.ylim([0, max(sm) * 1.2])

#plt.yticks([-8, -4, -0, 4], fontsize=25)
plt.xticks(range(5), fontsize=25)

strip_axes(plt.gca())

tstep = len(sm)/4
hrange = range(0, len(sm)+1, tstep)
plt.xticks(hrange, range(5))

plt.show()
