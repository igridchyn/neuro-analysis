#!/usr/bin/env python2

from numpy.polynomial.polynomial import polyfit
from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
from scipy.stats import pearsonr, wilcoxon, spearmanr

if len(argv) < 5:
    print 'USAGE: (1)<sleepcat file list> (2)<beh measure> (3)<sleep measure number 0-3 [3 = number of inh]> (4)<beh value composition: 0=score, 1=conrtol, 2=target>'
    exit(0)

bm = argv[2]
smn = int(argv[3])

asleep = []
abeh = []

bc = int(argv[4])

for line in open(argv[1]):
    # load beh
    ws = line.split('/')

    # load sleep stat
    sc = np.loadtxt(line.strip())
    if smn == 3:
        inhpath = '../processing/%s/%s/13ssi/inh.timestamps' % (ws[1], ws[2])
        inhc = 0
        for line in open(inhpath):
            inhc += 1
        asleep.append(inhc)
    else:
        asleep.append(sc[smn])

    #print ws
    behpath = '../processing/%s/%s/16l/%s_%s_16l.whl.cbbeh' % (ws[1], ws[2], ws[1], ws[2])
    #beh = np.loadtxt(behpath)

    for lineb in open(behpath):
        ws = lineb.split(' ')
        if ws[0] == bm:
            cv = float(ws[1])
            tv = float(ws[2])

            if bm == 'ftpl':
                cv = np.log(cv)
                tv = np.log(tv)

            if bc == 0:
                abeh.append((cv-tv)/(cv+tv))
            elif bc == 1:
                abeh.append(cv)
            else:
                abeh.append(tv)

print asleep, abeh
#print np.corrcoef(asleep, abeh)[0,1]
pc = pearsonr(asleep, abeh)
#pc = spearmanr(asleep, abeh)
print 'PEARSON', pc

b,a = polyfit(asleep, abeh, 1)

plt.scatter(asleep, abeh)
plt.plot([min(asleep), max(asleep)], [b+a*min(asleep), b+a*max(asleep)], color='black')

LFS = 15
sleeplabs = ['Sleep % of REM', 'Sleep % of AWAKE', 'Sleep % of SLOW', 'Corr of SWR rate and theta power', 'Corr of SWE rate and delta power', 'Mean Delta power', 'Mean SWR frequency', '% of HSE in REM', 'INHIBIRED % in REM', 'Number of HSE', 'Number of disrupted HSE']
plt.xlabel(sleeplabs[smn], fontsize=LFS)

bmdic = {'d10':'Dwell time', 'nc10':'Number of crossings', 'ftpl':'1st trial path length'}
bclab = ['score', 'control', 'target']
bm = bmdic[bm]
plt.ylabel('Behaviour (%s), ' % bclab[bc] + bm, fontsize=LFS)
#plt.title('Correlation=%.2f, p=%.2f' % (pc[0], pc[1]))
plt.title('Rank order correlation=%.2f, p=%.2f' % (pc[0], pc[1]))

# plt.savefig('/home/igor/Pictures/19-10-25/BEH_VS_SLEEP_%s(%s)_%s.png' % (bm.replace(' ', '_'), bclab[bc], sleeplabs[smn].replace(' ', '_')))

# write correlation and std to file (append to plot all together later)
fvsstat = open('beh_vs_sleep_stats.txt', 'a')
cci = corr_conf_interval(pc[0], 21, 1.96)
fvsstat.write('%f %f %f %f\n' % (pc[0], cci[0], cci[1], pc[1]))

# plt.show()
