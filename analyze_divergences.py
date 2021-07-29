#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats
import matplotlib.cm as cm
import matplotlib as mpl

if len(argv) < 2 :
	print('USAGE: (1)<file>')
	exit(0)

d = np.loadtxt(argv[1])

# STRUCTURE:
# 0-3     4-7      8-11   12                13                14           15        16             17                     18-19                 20-21       22-23
# 4 means, 4 maxs, 4 pfs, 1 d score - mean, 1 d score - max,  1 animal_id, 1 day_id, 1 paradigm_id, 1 score - mean unnorm, 2 mean scores - raw,  2 sparsity, 2 coherence
# max/means: s1-e1 s1-e2 s2-e1 s2-e2
# pfs: between 2 envs in S1    -    between 2 envs in S2    -    E1 across sessions    -    E1 across sessions

# paradigm / animal / day filter
# NO CBS
# ONLY LT / 4A : 1 / 2;
#   LT HAS NO POST!
PARADIGM = 1
#parfilt = d[:, 16] > -1
parfilt = (d[:, 16] == 0) | (d[:,16] == 0)
# cheesboards
#parfilt = (d[:, 16] == 0) | (d[:,16] == 3)

# score before
#befscore = np.abs(d[:, 18]) < 0.2
#befscore = np.abs(d[:, 19]) < 0.2

# sparsity (<0.3) / coherence (>0.5)
# BOTH
#scfilt = (d[:, 14] < 0.3) & (d[:,15] < 0.3) & (d[:,16] > 0.5) & (d[:,17] > 0.5)
# ANY
IND_SC = 20
scfilt = ((d[:, IND_SC] < 0.3) | (d[:, IND_SC+1] < 0.3)) & ((d[:, IND_SC+2] > 0.5) | (d[:, IND_SC+3] > 0.5))

# BY MAXIMUM RATE - doesn't make much difference
maxratefilt = np.maximum(d[:,0], d[:,1]) < 1000

# THOSE THAT REMAP - 0.5 MAKES IT WORSE
MAXPFS = 1.0
# THIS IMPROVES QUITE A BIT ! - FOR LT ONLY AND IN COMBINATION WITH OTHERS
MINPFS = 0.95
pfsfilt = (d[:,10] < MAXPFS) | (d[:,11] < MAXPFS)
#pfsfilt = (d[:,10] > MINPFS) | (d[:,11] > MINPFS)

allfilt = parfilt & scfilt & maxratefilt & pfsfilt
#allfilt = parfilt & scfilt & maxratefilt & pfsfilt & befscore

COL_CMP = 12
# score with different filters
for rate in [0, 0.1, 0.25, 0.5, 1, 3, 5]:
    # FILTER BY SESSION 1 RATES, MEAN
    scf = d[(np.minimum(d[:,0], d[:,1]) > rate) & allfilt, COL_CMP]
    print('SCORE WITH MIN MEAN RATE (BOTH) %.2f = %.2f, n=%d' % (rate, np.nanmean(scf), len(scf)))

    # FILTER BY SESSION 1 RATES - ANY, MEAN
    scf = d[(np.maximum(d[:,0], d[:,1]) > rate) & allfilt, COL_CMP]
    print('SCORE WITH MIN MEAN RATE (ANY) %.2f = %.2f, n=%d, p=%.4f' % (rate, np.nanmean(scf), len(scf), stats.ttest_1samp(scf, 0, nan_policy='omit')[1]))

    # FILTER BY SESSION 1 RATES - MAX
    scf = d[(np.minimum(d[:,4], d[:,5]) > rate) & allfilt, COL_CMP]
    print('SCORE WITH MIN MAX RATE (BOTH) %.2f = %.2f, n=%d, p=%.4f' % (rate, np.nanmean(scf), len(scf), stats.ttest_1samp(scf, 0, nan_policy='omit')[1]))

    # FILTER BY SESSION 1 RATES - ANY, MAX
    scf = d[(np.maximum(d[:,4], d[:,5]) > rate) & allfilt, COL_CMP]
    print('SCORE WITH MIN MAX RATE (ANY) %.2f = %.2f, n=%d' % (rate, np.nanmean(scf), len(scf)))

    # FILTER BY SESSION 1 AND 2 RATES - ANY, MAX
    scf = d[(np.maximum(d[:,4], d[:,5]) > rate) & (np.maximum(d[:,6], d[:,7]) > rate) & (allfilt), COL_CMP]
    print('SCORE WITH MIN MAX RATE (ANY), BOTH SESSIONS %.2f = %.2f, n=%d' % (rate, np.nanmean(scf), len(scf)))

    scf = d[(np.maximum(d[:,0], d[:,1]) > rate) & (np.maximum(d[:,2], d[:,3]) > rate) & (allfilt), COL_CMP]
    print('SCORE WITH MIN MEAN RATE (ANY), BOTH SESSIONS %.2f = %.2f, n=%d' % (rate, np.nanmean(scf), len(scf)))

    scf = d[(np.minimum(d[:,0], d[:,1]) > rate) & (np.minimum(d[:,2], d[:,3]) > rate) & (allfilt), COL_CMP]
    print('SCORE WITH MIN MEAN RATE (BOTH), BOTH SESSIONS %.2f = %.2f, n=%d' % (rate, np.nanmean(scf), len(scf)))

print('WARNING: DIFFERENT RATE FILTER USED')
#anfilt = (np.maximum(d[:,0], d[:,1]) > 0.5) & allfilt
anfilt = (np.maximum(d[:,0], d[:,1]) > 1.0) & allfilt
scf = np.abs(d[anfilt,:][:, (18,19,16)])
np.savetxt('scores.txt', scf[:,(0,1)])


pars = [''] * len(scf)
pars = np.array(pars)
pars[(scf[:,2] == 0) | (scf[:,2] == 3)] = 'CB'
pars[scf[:,2] == 1] = 'LT'
pars[scf[:,2] == 2] = 'PLUS'

LFS = 30
# scores scatter
if False:
#if True:
    colors = ['red', 'blue', 'green', 'red']
    for p in [1,2]:
#    for p in [0,1,2,3]:
        scat = plt.scatter(scf[scf[:,2] == p,0], scf[scf[:,2] == p,1], c=colors[p])

#    plt.xlabel('Before sleep', fontsize=LFS)
#    plt.ylabel('After sleep', fontsize=LFS)
    plt.xlabel('1st learning block', fontsize=LFS)
    plt.ylabel('Last learning block', fontsize=LFS)
#    plt.title('Abs rate scores, LT+PLU+CB, rate>0.5', fontsize=LFS)
    plt.title('Abs rate scores, LT+PLUS, rate>0.5', fontsize=LFS)
    plt.legend(['LT', 'PLUS'], fontsize=LFS-5)
#    plt.legend(['CB', 'LT', 'PLUS'], fontsize=LFS-5)
    plt.show()

# lines: rate before to rate after in each environment
# maxs
#rba = d[anfilt, :][:,(4,5,6,7,13)]
# means
rba = d[anfilt, :][:,(0,1,2,3,12)]

# to check the range
#plt.hist(rba[:,4])
#plt.show()

low = np.percentile(rba[:,4], 5)
high = np.percentile(rba[:,4], 95)
# range -0.8 to 0.6
norm = mpl.colors.Normalize(vmin=low, vmax=high)
cmap = cm.jet
m = cm.ScalarMappable(norm=norm, cmap=cmap)

#plt.figure()
for c in range(len(rba)):
    plt.arrow(rba[c,0], rba[c,1], rba[c,2]-rba[c,0], rba[c,3]-rba[c,1], head_width=0.2, color=m.to_rgba(rba[c,4]))

#PAR = 'PLUS'
PAR = 'PLUS'
RMAX = 15
plt.xlim(0, RMAX)
plt.ylim(0, RMAX)
plt.plot([0,RMAX], [0,RMAX], color='black')
plt.gcf().set_size_inches(18, 18)
plt.xlabel('Mean rate ENV 1', fontsize = LFS)
plt.ylabel('Mean rate ENV 2', fontsize = LFS)
if '2_4' in argv[1]:
    plt.title('Rate change bef->aft sleep, color=abs score diff, ' + PAR, fontsize = LFS)
else:
    plt.title('Rate change during learning (1st block -> last block), color=abs score diff, ' + PAR, fontsize = LFS)
plt.tight_layout()
plt.show()
