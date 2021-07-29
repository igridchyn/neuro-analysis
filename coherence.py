#!/usr/bin/env python

import numpy as np
from sys import argv
import os
from matplotlib import pyplot as plt

def coherence_half(pf):
    means = np.zeros(pf.shape)
    means[:] = np.nan

    for y in range(1, pf.shape[0] - 1):
        for x in range(1, pf.shape[1] - 1):
            #if np.isnan(pf[y, x]) or np.isinf(pf[y, x]) or pf[y, x] == 0:
            #    continue

            sub = pf[y-1:y+2, x-1:x+2]
            if np.sum(~np.isnan(sub)) > 7:
                means[y,x] = (np.nansum(sub) - pf[y, x]) / (np.sum(~np.isnan(sub)) - 1)

    fpf = pf.flatten()
    fmeans = means.flatten()
    inds = ~np.isnan(fpf) & ~np.isnan(fmeans) & ~np.isinf(fpf) & ~np.isinf(fmeans)

    if np.sum(inds) != 0:
        coh = np.corrcoef(fpf[inds], fmeans[inds])[0, 1]
    else:
        coh = 0

    return coh

if len(argv) < 4:
    print('USAGE: (1)<base (pf_)> (2)<session> (3)<output file e1> (4 - OPTIONAL)<output file e2>')
    exit(0)

base = argv[1]
session = argv[2]
output1 = argv[3]
if len(argv) > 4:
    output2 = argv[4]
    SPLIT = True
else:
    SPLIT = False

c = 1

fout1 = open(output1, 'w')
if SPLIT:
    fout2 = open(output2, 'w')

occ = np.genfromtxt(base + 'occ_' + session + '.mat')
OT = 10

pfpath = base + str(c) + '_' + session + '_nosm.mat'
while os.path.isfile(pfpath):
    pfboth = np.genfromtxt(pfpath)
    halfx = pfboth.shape[1] // 2 if SPLIT else pfboth.shape[1]

    pfboth[np.isinf(pfboth)] = np.nan
    #pf[pf == 0] = np.nan
    pfboth[occ < OT] = np.nan

    # use only 1 half of the PF
    #try:
    #    imaxx = np.nanargmax(pf) % pf.shape[1]
    #    print 'argmax-x: %d' % imaxx
    #    if imaxx >= halfx:
    #        pf[:, :halfx] = np.nan
    #    else:
    #        pf[:, halfx:] = np.nan
    #except:
    #    print 'Nan only'

    pf1 = pfboth[:, :halfx]
    coh1 = coherence_half(pf1)
    coh2 = 0
    if SPLIT:
        pf2 = pfboth[:, halfx:]
        coh2 = coherence_half(pf2)

    print(str(c), ' coherences: ', coh1, coh2)

    c += 1
    pfpath = base + str(c) + '_' + session + '_nosm.mat'

    fout1.write(str(coh1) + '\n')
    if SPLIT:
        fout2.write(str(coh2) + '\n')

