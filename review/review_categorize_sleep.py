#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 6:
    print 'USAGE: (1)<SWR timestamps> (2)<theta/delta ratio - minutewise> (3)<REM t/d threshold> (4)t/d by SWR rate threshold for AWAKE (5)<output file - 3 numbers: % of REM, AWAKE, SLOW sleep> (6)<OPT: theta> (7)<OPT: delta> (8)<OPT: sw depth>'
    print 'Categorize sleep periods according to SWR frequency and THETA/DELTA ratio'
    print 'OUTPUT: %REM - %AWAKE - %SLOW - CORR(SWRRATE, THETA POWER) - CORR(SWRRATE, DELTA POWER)'
    exit(0)

# argv = resolve_vars(argv)

swrt = np.loadtxt(argv[1])
tdrat = np.loadtxt(argv[2])
remthold = float(argv[3])
awakethold = float(argv[4])
outpath = argv[5]

if os.path.isfile('tdthold'):
    print 'WARNING: override REM theta-delta threshold...'
    remthold = np.loadtxt('tdthold')

if len(argv) > 6:
    thetas = np.loadtxt(argv[6])
if len(argv) > 7:
    deltas = np.loadtxt(argv[7])
if len(argv) > 8:
    swdepth = np.loadtxt(argv[8])

# calclulate SWR rate by minute

swrper = 24000 * 60

swrminhz = [0] * len(tdrat)#swt[-1][-1] / swrper
t = 0
iswrt = 0

for i in range(len(swrt)):
    swrmin = int(swrt[i, 1] / swrper)
    if swrmin >= len(swrminhz):
        break
    swrminhz[swrmin] += 1.0

# load inh and ninh -> compile list of rates : total and inhibited
inht = np.loadtxt('inh.timestamps')
ninht = np.loadtxt('ninh.timestamps')
# !!!!!
hset = np.concatenate((inht, ninht))
hse = [0] * len(tdrat)
for inh in hset:
    hsemin = int(round(inh / float(swrper)))
    if hsemin >= len(hse):
        continue
    hse[hsemin] += 1.0
#hsehz /= 60.0

inh = [0] * len(tdrat)
for it in inht:
    inhmin = int(round(it / float(swrper)))
    if inhmin >= len(inh):
        continue
    inh[inhmin] += 1.0

swrminhz = np.array(swrminhz, dtype=float)
swrminhz /= 60.0

np.savetxt('swrrate', swrminhz)

# NOW THRESHOLD THE REM
# ??? also use low SWR rate here ???
indrem = tdrat > remthold
remper = np.sum(indrem) / float(len(tdrat))

# % OF HSE IN REM
hse = np.array(hse)
hseremper = np.sum(hse[indrem]) / float(len(hset))
inh = np.array(inh)
inhremper = np.sum(inh[indrem]) / float(len(inht))# np.sum(inh)

# THRESHOLD AWAKE
#swrminhz[swrminhz == 0] = 0.01
indwake = ((tdrat / swrminhz) > awakethold) & ~indrem
awakeper = np.sum(indwake) / float(len(tdrat))

LFS = 15
if len(argv) > 6:
    #plt.figure(figsize=(12,8))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15,8))
    #swrminhz[swrminhz == 0.01] = 0.05
    ax1.plot(swrminhz)
    if len(argv) > 8:
        ax1_2 = ax1.twinx()
        ax1_2.plot(swdepth, color = 'black')
        ax1_2.legend(['SW depth'], fontsize=LFS, loc='upper right')
    else: # theta delta
        ax1_1 = ax1.twinx()
        ax1_1.plot(thetas/deltas, color='green')
        ax1_1.legend(['Theta/Delta'], fontsize = LFS, loc='upper right')

    ax1.legend(['SWR rate'], fontsize=LFS, loc='upper left')
    ax1.grid()
    # ax2 = plt.gca().twinx()
    ax2.plot(swrminhz, color='blue')
    ax2.legend(['SWR rate'], fontsize=LFS, loc='upper left')
    ax2_1 = ax2.twinx()
    ax2_1.plot(thetas, color='green')
    ax2_1.plot(deltas, color='red')
    ax2_1.grid()
    ax2_1.legend(['Theta power', 'Delta power'], fontsize=LFS, loc='upper right')

    day = argv[2].split('_')[1]
    suf = argv[-1][-2:] if '_' in argv[-1] else ''

    plt.suptitle(day + suf)
    plt.savefig('/home/igor/Pictures/19-10-16/SLEEPCAT_%s%s.png' % (day, suf))

    #plt.show()
else:
    # VALIDATE
    plt.figure(figsize=(12,8))
    #swrminhz[swrminhz == 0.01] = 0.05
    plt.plot(swrminhz)
    plt.plot(tdrat / swrminhz / 20.0, color='green')
    plt.legend(['SWR rate','TD / SWR'])
    ax2 = plt.gca().twinx()
    ax2.plot(tdrat, color='red')
    plt.legend(['T/D ratio'])
    #plt.show()

# REST = slow-wave sleep
slowper = 1 - awakeper - remper

print 'SLEEP PERCENTAGES: REM/AWAKE/SLOW', remper, awakeper, slowper
fo = open(outpath, 'w')
fo.write('%f\n%f\n%f' % (remper, awakeper, slowper))

if len(argv) > 6:
    thetas = thetas[:len(swrminhz)]
    deltas = deltas[:len(swrminhz)]
    print 'Array sizes: ', len(swrminhz), len(thetas)
    print 'Correlations of swr rate and theta / delta power:'
    print '           ', np.corrcoef(swrminhz, thetas)[0,1], np.corrcoef(swrminhz, deltas)[0,1]
    fo.write('\n%f\n%f' % (np.corrcoef(swrminhz, thetas)[0,1], np.corrcoef(swrminhz, deltas)[0,1]))

    fo.write('\n%f\n%f\n%f\n%f\n%d\n%d' % (np.nanmean(deltas[~indrem]), np.mean(swrminhz[~indrem]), hseremper, inhremper, len(hset), len(inht)))

# SWR depth is useless - uncorrelated with anything ...
#if len(argv) > 8:
#    print 'Correlations of SWR depth and SWR rate:'
