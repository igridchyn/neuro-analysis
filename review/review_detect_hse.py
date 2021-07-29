#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
import subprocess

def detect_hses():
    # window start
    t = 0
    ires = 0
    # hse window starts (with >=peak avg rate)
    hse = []
    while t + WIN < res[-1]:
        nwin = 0
        while ires < len(res) and res[ires] < t + WIN:
            nwin += 1
            # FILTER OUT INS IF NEED
            ires += 1

        wrate = nwin / WIN
        if wrate > PFAC * tavg:
            hse.append(t)
            # cooldown
            t += COOLDOWN - WIN
            while ires < len(res) and res[ires] < t + WIN:
                ires += 1

        t += WIN
    return hse
#=========================================================================

if len(argv) < 4:
    print 'USAGE: (1)<data dir that contains: configuration file with synchrony tetrodes, res/clu/fet/cluster_shifts, ninh.timestamps> (2)<time window for detection, ms> (3)<file with hse timestamps>'# (3)<detection peak factor>'
    print 'DETECT HSE BASE ON OVERALL INSTANT RATE OF RES/FET SPIKES AND TETRODES IN THE REALTIME CONFIG'
    exit(0)

argv = resolve_vars(argv)

# parse synchrony tetrodes from 13ssi conf
# ? use clustered data ?

BASE = argv[1]
WIN = float(argv[2]) * 24
#PFAC = float(argv[3])
COOLDOWN = 5 * WIN

# JUST USE ALL CLUSTERED SPIKES FOR NOW ... - may be except interneurons ?
#res = subprocess.check_output(["grep", '-A', '1', 'Synchrony tetrodes',  '%s13ssi_1_rec.log' % BASE])
#tetlist =  res.split('\n')[1]

clu = np.loadtxt(BASE + 'clu', dtype=int)
res = np.loadtxt(BASE  +'res', dtype=float)
hses = np.loadtxt(argv[3], dtype = int)

# EXCLUDE INTERNEURONS
rates = []
for i in range(max(clu)):
    rates.append(np.sum(clu == i) * 24000 / res[-1])
#print sorted(rates)
#exit(0)

MAXRATE = 20
ins = [i for i in range(max(clu)) if rates[i] > MAXRATE]
print ins
ind = [True] * len(clu)
for ine in ins:
    ind = ind & (clu != ine)
res = res[ind]
clu = clu[ind]
#exit(0)

# overall average firing rate : spikes / sample
tavg = len(clu) / res[-1]

# CALCULATE MEAN AND STD RATES IN GIVEN WINDOW


#hse = detect_hses()
#print len(hse), 'events detected'

# calculate synchrony around loaded events
ires = 0
# TRAD = 200 * 24 # was 200*24 OR 1000*24
TRAD = 10 * int(WIN)
totsync = [0.0] * (TRAD * 2 / int(WIN)) 
for hse in hses:
    while ires < len(res) and res[ires] < hse - TRAD:
        ires += 1

    # calculate synchrony in every window
    for iwin in range(2 * TRAD / int(WIN)):
        # calc sync in iwin-th window from hse-TRAD on
        nspike = 0
        while ires < len(res) and res[ires] < hse - TRAD + (iwin+1) * WIN:
            nspike += 1
            ires += 1

        totsync[iwin] += nspike

# norm by average:
totsync = np.array(totsync)
totsync /= WIN
totsync /= len(hses)
totsync /= tavg

plt.plot(totsync)
plt.show()
