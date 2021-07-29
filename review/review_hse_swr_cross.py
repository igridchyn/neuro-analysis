#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
import glob

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

def merge_arrs(a, b):
    ia = 0
    ib = 0
    me = []
    while ia < len(a) and ib < len(b):
        if a[ia] < b[ib]:
            me.append(a[ia])
            ia += 1
        else:
            me.append(b[ib])
            ib += 1

    if ia < len(a):
        me.extend(list(a[ia:]))
    else:
        me.extend(list(b[ib:]))

    return np.array(me)

def cross_corr(a, b):
    ia = 0
    ib = 0

    cc = [0] * (2 * nbin + 10)

    while a[ia] < bs * nbin:
        ia += 1

    # cross: a - b
    ibs = 0
    while ia < len(a):
        ib = ibs
        # OOR
        # - 42 for average delay in processing between detection and response;
        # -153 for half of SWr detection filter width - need data for the second half to get ...
        while ib < len(b) and  b[ib] < a[ia] - bs * nbin - 42 - 153:
            ib += 1
        ibs = ib

        # print ib, ia
        while ib < len(b) and b[ib] < a[ia] + bs * nbin - 42 - 153:
            bn = (a[ia] - b[ib] + 42 + 153) / bs + nbin
            cc[bn] += 1
            ib += 1

        ia += 1

    return np.array(cc).astype(float)

if len(argv) < 3:
    print 'USAGE: (1)<file with directories list> (2)<which events: inh, ninh or both>'
    print 'Plot cross-correlogramm of HSEs and SWRs for all days'
    exit(0)

# bin size
bs = 24 * 10
# number of bins - on every side
nbin = 50

events = argv[2]

dirlistpath = argv[1]
ct = np.array([0.0] * (2 * nbin + 10)) 
cti = np.array([0.0] * (2 * nbin + 10)) 

nhse = 0.0
nday = 0.0
nswr = 0.0

ccs = []

for line in open(dirlistpath):
    dirp = line.strip()
    swrs = np.loadtxt(glob.glob(dirp + '*13ssi.*sw')[0], dtype=int)[:,1]
    inh = np.loadtxt(dirp + 'inh.timestamps', dtype=int)
    ninh = np.loadtxt(dirp + 'ninh.timestamps', dtype=int)

    if events == 'inh':
        hses = inh
    elif events == 'ninh':
        hses = ninh
    else:
        hses = merge_arrs(inh, ninh)

    cc = cross_corr(swrs, hses) # / float(len(swrs))
    ct += cc
    ccs.append(cc / len(swrs))
#   ct += cross_corr(hses, swrs) / float(len(swrs))

    cti += cross_corr(swrs, inh)

    nday += 1
    nswr += len(swrs)
    nhse += len(hses)

# for stds
ccs = np.array(ccs)
# ccs /= # nswr
ccstds = np.std(ccs, 0)
ccstds /= np.sqrt(21)

print 'STDs shape: ', ccstds.shape
print ccstds

ct = ct.astype(float)
#ct /= np.sum(ct)
#ct /= nhse
print nswr
ct /= nswr
ctcum = np.cumsum(ct)

cti = cti.astype(float)
cti /= np.sum(cti)
ctcumi = np.cumsum(cti)

# plot cross
#plt.bar(range(len(ct)), ct)
LFS = 25

plt.figure(figsize = (8, 4))
# step was 2, ADJSUT MIN/MAX TOO
# 2 MS STEP
#xr = range(-2*nbin,2*(nbin+10), 2)
xr = range(-10*nbin+5,10*(nbin+10)+5, 10)
print len(xr), len(ct)
plt.bar(xr, ct, width=bs/24*0.75, color='red' if events == 'inh' else 'b')
plt.errorbar(xr, ct, yerr = ccstds, color='black', fmt = '.')
# for cumulative
#plt.plot(range(-2*nbin,2*(nbin+10),2), ctcum, linewidth=5)

# FOR BOTH
#plt.plot(range(-2*nbin,2*(nbin+10),2), ctcumi, linewidth=5, color='red')
#plt.legend(['Control events', 'Inhibited events'], fontsize=15)
#plt.title('Disrupted events', fontsize=25)
tit = 'All HSE' if events == 'both' else ('Disrupted HSE' if events == 'inh' else 'Control HSE')
# as 'All events'
plt.title(tit, fontsize=LFS)

plt.axvline(x=0, color='black', linewidth=1)
#plt.xlabel('T(SWR)-T(HSE)', fontsize=LFS)
plt.xlabel('t, ms', fontsize=LFS)
#plt.ylabel('CDF(Cross-correlation)', fontsize=LFS)
plt.ylabel('Cross-correlation', fontsize=LFS)
plt.xticks(range(-10*nbin,10*nbin+1, 100))
strip_axes(plt.gca())

plt.gca().locator_params(nbins=5, axis='y')
set_yticks_font(LFS)
set_xticks_font(LFS)

# 0.11 if disrutped + control
#plt.ylim([0, 0.11])
plt.ylim([0, 0.16])

#plt.xlim([-500, 520])
#plt.xlim([-300, 320])
plt.xlim([-200, 200])
plt.tight_layout()

plt.show()
