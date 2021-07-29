#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 3:
	print 'USAGE: (1)<list of dirs> (2)<INTERVAL, MIN>'
	exit(0)

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

minint = int(argv[2])
tint = 24000 * 60 * minint

# ratios of control / raget
nsamp = (4 * 3600 * 24000 / tint + 2)

# NUMBER of target / control
ntarg = [0] * nsamp
ncont = [0] * nsamp

ntarg = np.array(ntarg)
ncont = np.array(ncont)

rats = np.zeros((nsamp))

nday = 0

ntargs = []
nconts = []

for d in open(argv[1]):
    ninh = np.loadtxt(d.strip() + '/ninh.timestamps', dtype=int)
    # do with all inh as well
    inh = np.loadtxt(d.strip() + '/inh_top20.timestamps', dtype=int)
    #inh = np.loadtxt(d.strip() + '/inh.timestamps', dtype=int)

    dntarg = np.zeros((nsamp), dtype=int)
    dncon = np.zeros((nsamp), dtype=int)

    for t in ninh:
        ind = t / tint
        # print ind, dncon
        dncon[ind] += 1

    for t in inh:
        ind = t / tint
        dntarg[ind] += 1

    #drat = [dntarg[i] / float(dncon[i]) if dncon[i] > 0 else 0 for i in range(len(dncon))]
    #drat = [np.log(dntarg[i] / float(dncon[i])) if dncon[i] > 0 else 0 for i in range(len(dncon))]
    #drat = [np.log(dntarg[i] / float(dntarg[i] + dncon[i]))  for i in range(len(dncon))]
    drat = [dntarg[i] / float(dntarg[i] + dncon[i])  for i in range(len(dncon))]
    drat = np.array(drat)
    rats += drat

    ntarg += dntarg
    ncont += dncon

    ntargs.append(dntarg)
    nconts.append(dncon)

    nday += 1

ntarg /= nday
# ntarg /= 4 # to consider top 20% only
ncont /= nday

ntargs = np.array(ntargs)
nconts = np.array(nconts)
stdtargs = np.std(ntargs, 0) / np.sqrt(21)
stdconts = np.std(nconts, 0) / np.sqrt(21)

LW = 5
LFS = 25
x = range(minint, nsamp * minint, minint)
#plt.plot(x, rats[ :-1], linewidth = LW)
plt.plot(x[:-1], ncont[:-2], linewidth = LW)
yup = ncont[:-2] + stdconts[:-2]
ydown = ncont[:-2] - stdconts[:-2]
plt.fill_between(x[:-1], ydown, yup, color='blue', alpha=0.3)
#plt.ylim([0, max(rats[:-1]) * 1.1])
#plt.legend(['Ratio target / control'], loc='lower left', fontsize = LFS-5)
plt.ylabel('Ratio target / control', fontsize = LFS)
plt.xlabel('Sleep time, h', fontsize = LFS)
plt.ylim([0, max(ncont) * 1.2])

# axc = plt.gca().twinx()
axc = plt.gca()

axc.plot(x[:-1], ntarg[:-2], color='red', linewidth = LW)
yup = ntarg[:-2] + stdtargs[:-2]
ydown = ntarg[:-2] - stdtargs[:-2]
plt.fill_between(x[:-1], ydown, yup, color='red', alpha=0.3)
axc.legend(['Control', 'Target'], loc='best', fontsize = LFS)
# axc.set_ylim([0, max(ntarg[:-1]) * 1.1])
plt.ylabel('Number of HSE', fontsize=LFS)
strip_axes(plt.gca())
plt.xticks(range(0, 241, 60), [0, 1, 2, 3, 4])
set_xticks_font(LFS)
set_yticks_font(LFS)

plt.tight_layout()
plt.show()
