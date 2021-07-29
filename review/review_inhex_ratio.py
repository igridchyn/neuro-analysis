#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
import random

if len(argv) < 5:
	print 'USAGE: (1)<dir list> (2)<reg frs> (3)<pres frs> (4)<int inds>'
	exit(0)

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

sd = os.getcwd()

ei_scores = []
ei_cints = []

eis_reg = []
eis_pres = []

for line in open(argv[1]):
    dpath = line.strip()

    os.chdir(dpath)
    resps = resolve_vars(argv)

    rfrs = np.loadtxt(resps[2])
    pfrs = np.loadtxt(resps[3])
    rfrs[0] = 0
    pfrs[0] = 0

    # load IN indices
    innum = np.loadtxt(argv[4], dtype=int)
    if innum.ndim == 0:
        innum = [innum]

    inind = [False] * len(rfrs)
    for num in innum:
        # ADDITIONALLY - RATE FILTER
        if pfrs[num] > 10:
            inind[num] = True
    inind = np.array(inind)

    # calculate ratios
    pyrind = ~inind # & (rfrs < 5) & (pfrs < 5) & (rfrs > 0.5) & (pfrs > 0.5)

    ei_reg = np.mean(rfrs[inind]) / np.mean(rfrs[pyrind])
    ei_pre = np.mean(pfrs[inind]) / np.mean(pfrs[pyrind])

    eis_reg.append(1.0/ei_reg)
    eis_pres.append(1.0/ei_pre)

    # DEBUG
    print 'Ratios:', ei_reg, ei_pre , 'means:', np.mean(rfrs[inind]), np.mean(rfrs[~inind]), np.mean(pfrs[inind]), np.mean(pfrs[~inind])

#    if np.sum(inind) < 2:
#        print 'WARNING: ignore day because of little INs'
#        os.chdir(sd)
#        continue

    # score
    #ei_score = 2*(ei_pre - ei_reg) / (ei_pre+ei_reg)
    ei_score = (ei_pre - ei_reg) / ei_reg

    # get bootstrapping confidence interval for the score
    bscores = []
    nsamp = 20
    i = 0
    while i < nsamp:
        i += 1
        # sample interneurons
        irates_r = []
        irates_p = []
        for ni in range(len(innum)):
            rind = random.randint(0, len(innum) - 1)
            irates_r.append(rfrs[innum[rind]])
            irates_p.append(pfrs[innum[rind]])

        rfrs_pyr = rfrs[~inind]
        pfrs_pyr = pfrs[~inind]
        prates_r = []
        prates_p = []
        for nup in range(len(rfrs_pyr)):
            rind = random.randint(0, len(rfrs_pyr) - 1)
            prates_r.append(rfrs_pyr[rind])
            prates_p.append(pfrs_pyr[rind])

        # scores
        #ei_reg_b =  np.mean(prates_r) / np.mean(irates_r)
        #ei_pre_b =  np.mean(prates_p) / np.mean(irates_p)
        ei_reg_b =  np.mean(irates_r) / np.mean(prates_r)
        ei_pre_b =  np.mean(irates_p) / np.mean(prates_p)

        # ignore nans
        if np.isnan(ei_reg_b) or np.isnan(ei_pre_b) or (ei_pre_b + ei_reg_b) == 0:
            print ei_reg_b, ei_pre_b
            i -= 1
            continue

        ei_score_b = 2*(ei_pre_b - ei_reg_b) / (ei_pre_b + ei_reg_b)
        bscores.append(ei_score_b)

    bscores = sorted(bscores)

    # DEBUG
    ilow = nsamp / 20
    ihigh = nsamp - nsamp/20
    if bscores[ilow] > bscores[ihigh]:
        print bscores

    cint = [bscores[ilow], bscores[ihigh]]
    ei_cints.append(cint)

    print ei_score, 'CI=', cint, dpath

    if not np.isnan(ei_score):
        ei_scores.append(ei_score)

    os.chdir(sd)

print 'Wilcoxon:', stats.wilcoxon(eis_reg, eis_pres)
print 'Score mean / std', np.nanmean(ei_scores), np.nanstd(ei_scores)
rm = np.nanmean(eis_reg)
pm = np.nanmean(eis_pres)
rs = np.nanstd(eis_reg)
ps = np.nanstd(eis_pres)
print 'Before m/s; after m/s', np.nanmean(eis_reg), np.nanstd(eis_reg), np.nanmean(eis_pres), np.nanstd(eis_pres)

ei_cints = np.array(ei_cints).transpose()
print ei_cints.shape

FS = 25

plt.figure(figsize = (3,5))

#plt.boxplot(ei_scores, boxprops= dict(linewidth=3.0, color='black'), whiskerprops=dict(linestyle='-',linewidth=3.0, color='black'))
plt.bar([0], [rm])
plt.bar([1], [pm], color='orange')
plt.legend(['Light pulses', 'Pre-rest'], fontsize = 15)
plt.errorbar([0, 1], [rm, pm], yerr = [rs/np.sqrt(20), ps/np.sqrt(20)], fmt='.', linewidth = 4, color='black')

plt.xticks([])
#plt.ylabel('I/E change score', fontsize=FS)
plt.ylabel('E/I rate', fontsize=FS)
plt.gca().locator_params(nbins=5, axis='y')
strip_axes(plt.gca())
set_yticks_font(FS)
plt.tight_layout()
plt.show()


# =====
x = range(len(ei_scores))
plt.bar(x, ei_scores)
plt.errorbar(x, ei_scores, yerr = ei_cints, fmt='.', linewidth=4, color='black')
plt.title('Change in I/E ratio from\nregular pulses to pre-sleep', fontsize = FS+5)
plt.xlabel('Session', fontsize=FS)
plt.xticks([])
#plt.ylabel('I/E change score', fontsize=FS)
plt.ylabel('E/I rate', fontsize=FS)
plt.gca().locator_params(nbins=5, axis='y')
strip_axes(plt.gca())
set_yticks_font(FS)
plt.tight_layout()
plt.show()

#print np.mean(ei_scores)
#plt.hist(ei_scores)
#plt.show()
