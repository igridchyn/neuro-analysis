#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
import struct

def extract_spike_times():
    tetr = 0
    fsfet = []
    for tetr in range(len(PCNS)):
        fsfet.append(open(BASE + str(tetr)))

    # initial read of single spike
    BIG = 400000000
    ts = []
    for tetr in range(len(PCNS)):
        FETN = PCNS[tetr] + 4
        fmt = FETN * 'f' + 'i'
        struct_size = 4 * (FETN + 1)
        spikebin = fsfet[tetr].read(struct_size)

        if not spikebin:
            ts.append(BIG)
        else:
            fet = struct.unpack(fmt, spikebin)
            ts.append(fet[-1])

    allt = []
    repint = 24000*60*10
    replast = 0
    while min(ts) < BIG:
        tetr = np.argmin(ts)
        allt.append(ts[tetr])

        if ts[tetr] > replast + repint:
            print 'Progress:', ts[tetr]
            replast = ts[tetr]

        FETN = PCNS[tetr] + 4
        fmt = FETN * 'f' + 'i'
        struct_size = 4 * (FETN + 1)
        spikebin = fsfet[tetr].read(struct_size)

        if not spikebin:
            ts[tetr] = BIG
        else:
            try:
                fet = struct.unpack(fmt, spikebin)
                ts[tetr] = fet[-1]
            except:
                print 'ERROR unpacking on tetr', tetr

    # np.savetxt(BASE + 'allt', allt)
    np.save(BASE + 'alltb', allt)

#=====================================================================

if len(argv) < 2:
    print 'USAGE: (1)<base for fet> (2)<tetrode config> (3)<event timestamps>'
    exit(0)

argv = resolve_vars(argv)
BASE = argv[1]

# read tetrode config
ft = open(argv[2])
ntet = int(ft.readline())
PCNS = []
for i in range(ntet):
        PCNS.append(int(ft.readline()) * 2)
        ft.readline()
print 'Numbers of channels per tetrode:', PCNS

if not os.path.isfile(BASE + 'alltb.npy'):
    extract_spike_times()

# allt = np.loadtxt(BASE + 'allt', dtype = int)
#allt = np.loadtxt(BASE + 'allt')
allt = np.load(BASE + 'alltb.npy')
#allt = allt.astype(int)
print 'Loaded all spike timestamps'
#np.save(BASE + 'alltb', allt)

# QUICK HACK - to see in regaa
np.savetxt('tmpspiket', allt[:2000], fmt = '%d')

# detect HSE
# spikes / sample
meanfr = len(allt) / float(allt[-1])
print 'Mean spikes / sample:', meanfr

# window ENDS
hse = np.loadtxt(argv[3])

# thold = 3.5

# TEST - distribution of synchrony level ...
# 20 ms windows
win = 20 * 24

meanfrwin = meanfr * win

previt = 0

# 100 on both sides, so +- 200 ms
nwins = 100
winshift = 2 * 24

syncs = [[] for i in range(nwins * 2 + 1)]

previthse = 0

rephseint = 500
rephselast = 0
ihse = 0

# syncs.npy - for ninh.timestamps
DUMPBASE = argv[3] + '_syncstats' #'syncs'
# IGNORE
LOADSYNC = os.path.isfile('%s.npy' % DUMPBASE)

for hset in hse:
    if LOADSYNC:
        break

    ihse += 1
    if ihse > rephselast + rephseint:
        print 'HSE calc progress:', ihse
        rephselast = ihse

    it = previthse

    while it < len(allt) and allt[it] < hset - win - winshift * nwins:
        it += 1
    previthse = it

    # number of spikes in the window preceding HSE timestamp
    ish = nwins
    previt = it
    while ish > -nwins:
        it = previt

        while it < len(allt) and allt[it] < hset - win - winshift * ish:
            it += 1
        previt = it

        nspikes = 0
        while it < len(allt) and allt[it] < hset - winshift * ish:
            nspikes += 1
            it += 1
       
        # SCALED !
        syncs[ish + nwins].append(nspikes / meanfr / win)

        ish -= 1

    #syncs.append(nspikes / meanfr/ win)

if LOADSYNC:
    syncs = np.load('%s.npy' % DUMPBASE, allow_pickle=True)
    print 'Loaded syncs'
else:
    np.save(DUMPBASE, syncs)

# CALCULATE DURATION
durs = []
nwrong = 0
nearly = 0
nlate = 0
for i in range(len(syncs[1])):
    t = nwins
    if syncs[t][i] < 1:
        nwrong = 0
        continue

    while t > 0 and syncs[t][i] > 1:
        t -= 1

    if t <= 0:
        nearly += 1
        continue

    tstart = t
    t = nwins
    while t < len(syncs) and syncs[t][i] > 1:
        t += 1

    if t >= len(syncs):
        nlate += 1
        continue

    durs.append((t - tstart) * 2)

print 'WRONG, EARLY, LATE:', nwrong, nearly, nlate
fsstats = open(DUMPBASE + '.txt', 'w')
fsstats.write('%.3f %.3f %d' % (np.mean(durs), np.std(durs), len(durs)))

#plt.hist(durs, bins = 50)
#plt.show()

# print 'Mean sync level:', np.mean(syncs)

# NEED SAME BINS !
hsyncs = []

#plt.hist(syncs, 100)
for i in range(nwins * 2 + 1):
    hsyncs.append(np.histogram(syncs[i], bins=np.arange(1.5, 6.0, 0.5))[0])
#plt.plot(syncs[)
hsyncs = np.array(hsyncs)
plt.imshow(np.transpose(hsyncs))
#plt.xticks([0, 20, 40, 60, 80], ['-50', '-30', '-10', '10', '30'])
SH=0.5
plt.axvline(x=50+SH, linewidth=1, color='white')
plt.xticks([SH, 20+SH, 40+SH, 60+SH, 80+SH], ['-50', '-30', '-10', '10', '30'])
# plt.colorbar(orientation = 'horizontal')
plt.xlabel('Time relative to HSE detection, ms')
plt.ylabel('Synchrony, n*STD')

#plt.show()
