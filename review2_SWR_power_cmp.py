#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

def count_pow(filepath):
    pows = [0.0] * 10000
    lar = []
    pws = []

    fs = open(filepath)
    
    # index of the last SWR
    iswr = 0

    for ls in fs:
        if len(ls) < 20:
            hsetime = int(ls)
            continue

        # see if overlaps with SWR and define interval if it does
        #   consider +-40 ms = +-960 samples around SWR for power calculation - of 3600-6000 after HSE overlaps with this (within light period), then calculate power
        # also, require at least 120 samples overlap (1 full ripple, see below)

        minover = 20 * 24 # was 5 ms
        swrrad = 40 * 24 # was 40 ms

        while iswr < len(swrs) and swrs[iswr] + swrrad - minover < hsetime:
            iswr += 1

        if iswr >= len(swrs):
            break

        # if no overlap of at least one full ripple (200 Hz = 5ms => 120 samples), continue
        if swrs[iswr] - swrrad > hsetime + 2400 - minover:
            continue

        # now take overlap of 100ms after HSE and +-40ms of SWR
        tmin = max(hsetime, swrs[iswr] - swrrad)
        tmax = min(hsetime + 2400, swrs[iswr] + swrrad)
        imin = int(3600 + tmin - hsetime)
        imax = int(3600 + tmax - hsetime)

        rs = [int(s) for s in ls.split(' ')[:-1]]
        pw = 0
        npw = 0
        for r in rs[imin:imax]:                     # all light zone: 3600-6000
            if abs(r) < 10000:
                pw += r * r
                npw += 1
            if abs(r) < 10000 and abs(r) > 1500:
                pows[abs(r)] += 1
                lar.append(abs(r))
        pws.append(np.sqrt(pw / float(npw)))
    
    return pows, lar, pws

# =================================================================================================

if len(argv) < 2:
	print 'USAGE: (1)<dir list>'
	exit(0)

alllight = []
allnolight = []

allpwl = []
allpwnl = []

# count occurances of power - abs value 

for line in open(argv[1]):
    print line[:-1]
    if len(line) < 2:
        continue

    aipath = line[:-1] + '/ALL_NINH_EVENTS.sig'

    if not os.path.isfile(aipath):
        print aipath, 'does not exist, continue'
        continue

    swrs = np.loadtxt(line[:-1] + '/../13ssi/swrpeak')
    print '%d SWRs loaded' % len(swrs)

    (nolight_pow, nolight, pownl) = count_pow(aipath)
    (light_pow, light, powl) = count_pow(line[:-1] + '/ALL_INH_EVENTS.sig')

    alllight.extend(light)
    allnolight.extend(nolight)

    allpwl.extend(powl)
    allpwnl.extend(pownl)

    print 'Day KS of average power 2 samp:', stats.ks_2samp(powl, pownl)
    print 'Day MW of average power 2 samp:', stats.mannwhitneyu(powl, pownl)
    print 'Day TT of average power 2 samp:', stats.ttest_ind(powl, pownl)

    # break

#nolight_pow = np.array(nolight_pow, dtype=np.float32)
#light_pow = np.array(light_pow, dtype=np.float32)

#nolight_pow /= float(np.sum(nolight_pow))
#light_pow /= float(np.sum(light_pow))

#plt.plot(nolight_pow)
#plt.plot(light_pow)

xx = np.linspace(0, 5000, 1000)
kdel = stats.gaussian_kde(allpwl)
kdenl = stats.gaussian_kde(allpwnl)
plt.plot(xx, kdel(xx))
plt.plot(xx, kdenl(xx))
strip_axes(plt.gca())
plt.legend(['SWR within light', 'SWR outside light'])
plt.show()

#print 'KS 2 samp:', stats.ks_2samp(nolight, light)
print 'KS of average power 2 samp:', stats.ks_2samp(allpwl, allpwnl)

print 'Mean power aournd SWR in light/nolight', np.mean(allpwl), np.mean(allpwnl)
print 'MW-U Power around SWR in light/nolight', stats.mannwhitneyu(allpwl, allpwnl)

plt.show()
