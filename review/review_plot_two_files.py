#!/usr/bin/env python2

from numpy.polynomial.polynomial import polyfit
from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
from matplotlib import rcParams

# rcParams['font.family'] = 'Helvetica' # DOESN'T SHOW ERROR
#plt.rc('font', family='Helvetica') # not a proper family # DOESN'T SHOW ERROR

#font = {'family' : 'sans-serif',       'sans-serif':'Helvetica',        'weight' : 'normal',        'size'   : 18}
#plt.rc('font', **font)

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

if len(argv) < 4:
	print 'USAGE: (1)<dirs list> (2)<file name 1> (3)<file name 2> (4)<filt file>'
	exit(0)

fdirs = argv[1]
fname1 = argv[2]
fname2 = argv[3]
fnames = [fname1, fname2]

ffname = argv[4]

allvals1 = []
allvals2 = []
convlen = 250

# print 'WARNING: take THIRD OF VALUES ONLY !'

USESWAP = False
#USESWAP = True
print 'WARNING: USESWAP =', USESWAP

for line in open(fdirs):
    #print line
    if len(line) < 2:
            continue
    
    # READ WHICH ENV IS TARGET
    if USESWAP:
        for aline in open(line[:-1] + '/about.txt'):
            if aline.startswith('swap'):
                swap = bool(int(aline[-2]))
                #print swap
                break

    vals1 = np.loadtxt(line[:-1] + '/' + fname1, ndmin=1)
    vals2 = np.loadtxt(line[:-1] + '/' + fname2, ndmin=1)

    vals1 = np.array(vals1)
    vals2 = np.array(vals2)
   
#    print vals1.ndim, vals2.ndim
#    print type(vals1)

    if ffname != '-':
        intnum = np.loadtxt(line[:-1] + '/' + ffname)
        if intnum.ndim == 0:
            intnum = np.array([intnum])

        intnum = intnum.astype(int)
        # intnum = intnum.astype(bool)
        
        intind = [False] * len(vals1)
        for num in intnum:
            #intind[num - 1] = True
            intind[num-1] = True

        intind = np.array(intind)
        vals1 = vals1[~intind]
        vals2 = vals2[~intind]

    if USESWAP and swap:
        valst = vals1
        vals1 = vals2
        vals2 = valst

#    print line, vals1, vals2

#    vals = np.loadtxt(line[:-1] + '/' + fnames[int(swap)])

    # !!! 1st / last window of every SWR !!!
#    vals = vals[[3*i for i in range(len(vals)/3)]]
    #vals = vals[[(3*i+2) for i in range(len(vals)/3-1)]]
#    print len(vals)

    # FILTER - RATHER REPLACE !!!
    ind = (vals1 != 0) & (vals2 != 0) & ~np.isnan(vals1) & ~np.isnan(vals2)
    vals1 = vals1[ind]
    vals2 = vals2[ind]
    
    #vals = vals[~np.isinf(vals) & ~np.isnan(vals)]
    # vals[np.isinf(vals)] = np.nan

    #    if np.isinf(vals[0]) or np.isnan(vals[0]):
#        vals[0] = np.nanmean(vals)
#    for i in range(1, len(vals)):
#        if np.isinf(vals[i]) or np.isnan(vals[i]):
#            vals[i] = vals[i-1]

    # SMOOTH
#    vals = np.convolve(vals, [1.0/convlen] * convlen)[convlen:-convlen]

    # STANDARDIZE
#    vals = (vals - np.mean(vals)) / np.std(vals)

 #   if len(sm) == 0:
#        sm = vals
#    else:
#        nlen = min(len(sm), len(vals))
#        sm = sm[:nlen] + vals[:nlen]
    allvals1.extend(vals1)
    allvals2.extend(vals2)

#print sm

print allvals1, allvals2
print len(allvals1), len(allvals2)

allvals1 = np.array(allvals1)
allvals2 = np.array(allvals2)

# FILTER BOTH BY FIRST
MINR = 0.5 #0.5 #10
MAXR = 5 #5 #1000
print 'WARNINGL filter by MIN/MAX rate, first value:', MINR, MAXR
#ind = (allvals1 > MINR) & (allvals1 < MAXR) # & (allvals2 > MINR) & (allvals2 < MAXR)
ind = (allvals1 > MINR) & (allvals1 < MAXR) # & (allvals2 > MINR) & (allvals2 < MAXR)
#ind = (allvals1 > MINR) & (allvals1 < MAXR) | (allvals2 > MINR) & (allvals2 < MAXR)
allvals1 = allvals1[ind]
allvals2 = allvals2[ind]

# FOR RATE - REPOSNE PAIR
print 'Total ins:', len(allvals2)
print 'Inhibited ins', np.sum(allvals2 < -0.2877)
print 'Disinhibited ins', np.sum(allvals2 > 0.693)

print np.mean(allvals1),'+-', np.std(allvals1), np.mean(allvals2),'+-', np.std(allvals2)

print 'CORRELATION', stats.pearsonr(allvals1, allvals2)

# RESPONSE FILTER - TO COMPARE RATES INH/DINH
print 'WARINING: FILTER BY RESPONSE AND RATE MAX'
t1 = allvals1[(allvals2 < -0.2877)] # ALSO HAD RATE FILTER HERE BEFORE
t2 = allvals1[allvals2 > 0.693]
allvals1 = t1
allvals2 = t2
print 'REATES',  np.mean(allvals1),'+-', np.std(allvals1), np.mean(allvals2),'+-', np.std(allvals2)

print 'MWU:', stats.mannwhitneyu(allvals1, allvals2)
print 'ttest:', stats.ttest_ind(allvals1, allvals2)
print 'N:', len(allvals1), len(allvals2)

# INDEPENDENT FILTERING
#allvals1 = allvals1[allvals1 > MINR]
#allvals2 = allvals2[allvals2 > MINR]

std1 = np.std(allvals1) / np.sqrt(len(allvals1))
std2 = np.std(allvals2) / np.sqrt(len(allvals2))

PLOTFRVSRESP = False
if PLOTFRVSRESP:
    FSLAB = 30
    plt.scatter(allvals1, allvals2, s=1.5)
    plt.xlabel('Firing rate', fontsize = FSLAB)
    plt.ylabel('Light response', fontsize = FSLAB)
    b, m = polyfit(allvals1, allvals2, 1)
    min1 = min(allvals1)
    max1 = max(allvals1)
    plt.plot([min1, max1], [b+m*min1,b+m*max1], color='black')
    plt.show()

YLAB = 'Firing rate, Hz'
PLOTRATES = True

#TIT = 'Average firing rate\nduring learning'
TIT = 'Average firing rate\nduring end of learning'
#TIT = 'Average firing rate\nduring post-learning'
#TIT = 'Average firing rate\nduring probe'
#TIT = 'Firing rate and light response'

plt.figure(figsize=(5,5))

# FOR COMPARING RATES
if PLOTRATES:
    plt.bar([0], [np.mean(allvals1)], color=['blue'])
    plt.bar([2], [np.mean(allvals2)], color=['red'])
    #plt.legend(['CONTROL', 'TARGET'], fontsize=25)
    plt.errorbar([0],[np.mean(allvals1)], yerr = [std1], linewidth=4, color='black')
    plt.errorbar([2],[np.mean(allvals2)], yerr = [std2], linewidth=4, color='black')
    plt.xlim([-1, 3])

    #plt.yticks([0, 0.5, 1.0, 1.5], fontsize=25)
    #plt.yticks([0, 1.0, 2.0, 3.0], fontsize=25)
    # plt.xticks([],[])
    # plt.xticks([0, 2], ['Inhibited', 'Disinhibited'], fontsize=25)
    plt.xticks([0, 2], ['Control', 'Target'], fontsize=25)

    plt.ylabel(YLAB, fontsize = 35)
    plt.title(TIT, fontsize=25)

    strip_axes(plt.gca())
    set_yticks_font(25)
    # plt.ylim([0, 1.25]) # 1.65 for INH  DINH;  1.25 was used
    plt.gca().locator_params(nbins=5, axis='y')
    plt.tight_layout()
    #plt.subplots_adjust(left = 0.23)

    plt.show()
