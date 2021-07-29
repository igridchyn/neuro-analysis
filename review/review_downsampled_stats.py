#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
import random
from scipy import stats

if len(argv) < 6:
	print 'USAGE: (1)<PFSs control> (2)<PFSs target> (3)<out suf> (4)<scale CON> (5)<scale TARG>'
	exit(0)

SCC = float(argv[4])
SCT = float(argv[5])
OUTSUF = argv[3]
valcon = np.loadtxt(argv[1])
valtarg = np.loadtxt(argv[2])

valcon = valcon[~np.isnan(valcon)]
valtarg = valtarg[~np.isnan(valtarg)]

conmeans = []
targmeans = []
constds = []
targstds = []

NSAMP = 200
tps = []

for i in range(NSAMP):
    consamp = np.array([random.sample(valcon, 1) for i in range(len(valcon))])
    targsamp = np.array([random.sample(valtarg, 1) for i in range(len(valtarg))])

    # 1.15 / 1.1 2-3; 
    # reduce both
    consamp  *= SCC - random.random() / 5.0
    targsamp *= SCT  - random.random() / 5.0

    conmeans.append(np.mean(consamp))
    constds.append(np.std(consamp))
    
    targmeans.append(np.mean(targsamp))
    targstds.append(np.std(targsamp))

    #tps.append(stats.ttest_ind(consamp, targsamp)[1][0])
    tps.append(stats.mannwhitneyu(consamp, targsamp)[1])

np.savetxt('CONMEANS%s.txt' % OUTSUF, conmeans)
np.savetxt('CONSTDS%s.txt' % OUTSUF, constds)
np.savetxt('TARGMEANS%s.txt' % OUTSUF, targmeans)
np.savetxt('TARGSTDS%s.txt' % OUTSUF, targstds)

# do tests for each sample, scale if needed
#for s in range(NSAMP):
print 'Sorted p-values: ', sorted(tps)
