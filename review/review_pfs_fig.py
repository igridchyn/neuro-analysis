#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
import statsmodels
from scipy.stats import ks_2samp, mannwhitneyu

if len(argv) < 4:
	print 'USAGE: (1)<VALS CON> (2)<VALS TARG> (3)<TITLE>'
	exit(0)

valscon = np.loadtxt(argv[1])
valstarg = np.loadtxt(argv[2])

# SCALING
SCALE = 0.8
valscon *= SCALE
valstarg *= SCALE

title = argv[3]

# ASSUME 23 is given, load 24 and 25
avalscon = [valscon]
avalstarg = [valstarg]

for sub in ['INH', 'DINH']:
    avalscon.append(np.loadtxt(argv[1].replace('ALL', sub)) * SCALE)
    avalstarg.append(np.loadtxt(argv[2].replace('ALL', sub)) * SCALE)

ecdfcon = statsmodels.distributions.ECDF(valscon)
ecdftarg = statsmodels.distributions.ECDF(valstarg)

print 'KS test:', ks_2samp(valscon, valstarg)

title = title.replace(', ', '\n')

# GENERATE TITLE IF EMPTY
if title == '':
    if '23' in argv[1]:
        title = 'End-of-Learning vs. Probe'
    elif '24' in argv[1]:
        title = 'End-of-Learning vs. 1st Post-learning trial'
    elif '25':
        title = 'End-of-Learning vs. End-of-Post-Learning'
    else:
        title = '<Unrecognized Pair>'

#    if '_INH' in argv[1]:
#        title += 'Inhibited cells'
#    elif 'DINH' in argv[1]:
#        title += 'Disinhibited cells'
#    elif 'ALL' in argv[1]:
#        title += 'All cells'
#    else:
#        title += '<Unrecognized cell category>'

LFS = 25

fig = plt.figure(figsize=(12,8))

# BARS
for i in range(3):
    valscon = avalscon[i]
    valstarg = avalstarg[i]
    BTW = 4
    PULL = 0.3

    plt.bar([i*BTW + PULL], np.mean(valscon), color='blue')
    plt.bar([i*BTW+2- PULL], np.mean(valstarg), color='red')
    plt.legend(['Control', 'Target'], fontsize = 25, loc='lower left')
    plt.errorbar([i*BTW + PULL], np.mean(valscon), yerr=np.std(valscon), color='black', fmt='.')
    plt.errorbar([i*BTW+2 - PULL], np.mean(valstarg), yerr=np.std(valstarg), color='black', fmt='.')
    plt.ylabel('Place field similarity, r', fontsize=LFS)
    pval = mannwhitneyu(valscon, valstarg)[1]
    thei = 1.2 * max(np.mean(valscon), np.mean(valstarg))
    plt.text(i*BTW+1, 0.6, p_to_sig_str(pval), fontsize=30)
    # SAME FOR ALL
    plt.ylim([0, 0.7])

plt.xticks([1, BTW+1, 2*BTW+1], ['All', 'Inhibited', 'Disinhibited'], fontsize = 25)
plt.yticks(np.arange(0, 0.7, 0.2), fontsize=25)
#plt.gca().set_xticklabels(['Inhibited', 'Disinhibited', 'All'])

# FOR ECDF
#plt.plot(ecdfcon.x, ecdfcon.y)
#plt.plot(ecdftarg.x, ecdftarg.y, color='red')
#plt.xlabel('Place field similarity, r', fontsize=LFS)
#plt.ylabel('CDF(PFS)', fontsize=LFS)

plt.title(title, fontsize=25)
strip_axes(plt.gca())
# FOR CDF
#plt.subplots_adjust(left=0.11, bottom=0.13, right=0.99, top=0.9)
# FOR BARS
# WITHOUT LABELS
#plt.subplots_adjust(left=0.21, bottom=0.01, right=0.99, top=0.9)
# WITH LABELS
plt.subplots_adjust(left=0.10, bottom=0.05, right=0.99, top=0.9)

plt.savefig('/home/igor/Pictures/19-10-28/PFS/%s' % (argv[1].replace('CONMEANS', 'PFS').replace('txt', 'png')))

plt.show()
