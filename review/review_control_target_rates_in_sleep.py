#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 8:
	print 'USAGE: (1)<PFS file name - for rate and selectivity filtering> (2)<clu/res base - sleep> (3)<selectivity threshold> (4)<min FR> (5)<max FR> (6)<time window - min> (7)<list of directories>'
	exit(0)

# classify cells - Control / Target (based on end of learning mean firing rates - with minimal ratio and minimal rates ...)

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

pfsfile = argv[1]
crbase = argv[2]
SELTHOLD = float(argv[3])
MINR = float(argv[4])
MAXR = float(argv[5])
twmin = int(argv[6])
TW = twmin * 60 * 24000

nwin = 240 / twmin
mcrates = [0] * nwin
mtrates = [0] * nwin

allmcrates = [[] for i in range(nwin)]
allmtrates = [[] for i in range(nwin)]

topdir = os.getcwd()

cpath = 'SLEEP_RATES_C_REV5.txt'
tpath = 'SLEEP_RATES_T_REV5.txt'
LOAD = False

for ddir in open(argv[7]):
    if os.path.isfile(cpath):
        print 'READ RATES FROM FILE!'
        mcrates = np.loadtxt(cpath)
        mtrates = np.loadtxt(tpath)
        mcrates = np.array(mcrates)
        mtrates = np.array(mtrates)

        allmcrates = np.load(cpath + '.all.npy', allow_pickle = True)
        allmtrates = np.load(tpath + '.all.npy', allow_pickle = True)

        cstds = [np.std(allmcrates[i]) / np.sqrt(21) for i in range(len(allmcrates))]
        cstds = np.array(cstds)
        tstds = [np.std(allmtrates[i]) / np.sqrt(21) for i in range(len(allmtrates))]
        tstds = np.array(tstds)

        LOAD = True
        break

    ddir = ddir.strip()
    os.chdir(ddir)

    swap = int(resolve_vars(['', '%{swap}'])[1])
    pfs = np.loadtxt(pfsfile)
    # !!! E1 / E2 or C/T ?      use E1/E2 as CONTORL !!!
    crates = pfs[:,8]
    trates = pfs[:,9]

    if swap == 1:
        tmp = crates
        crates = trates
        trates = tmp

    icon = (crates > trates * SELTHOLD) & (crates > MINR) & (crates < MAXR)
    itar = (trates > crates * SELTHOLD) & (trates > MINR) & (trates < MAXR)

    coni = [i+1 for i in range(len(icon)) if icon[i]]
    tari = [i+1 for i in range(len(itar)) if itar[i]]

    print '%d control cells, %d target cells; swap: %d' % (len(coni), len(tari), swap)

    dcrbase = resolve_vars(['', crbase])[1]
    clu = np.loadtxt(dcrbase + 'clu', dtype = int)
    res = np.loadtxt(dcrbase + 'res', dtype = int)

    res = [res[i] for i in range(len(res)) if clu[i] in coni+tari]
    clu = [clu[i] for i in range(len(clu)) if clu[i] in coni+tari]

    # calulate rates in intervals
    iwin = 0
    ires = 0
    lastwin = 0
    while ires < len(res):
        nsc = 0
        nst = 0

        while ires < len(res) and res[ires] < lastwin + TW:
            if clu[ires] in coni:
                nsc += 1
            else:
                nst += 1
            ires += 1

        if iwin < len(mcrates):
            mcrates[iwin] += nsc / float(len(coni)) / (twmin * 60)
            mtrates[iwin] += nst / float(len(tari)) / (twmin * 60)

            allmcrates[iwin].append( nsc / float(len(coni)) / (twmin * 60))
            allmtrates[iwin].append( nst / float(len(tari)) / (twmin * 60))
        else:
            print 'WARNING: iwin >= len:', iwin

        lastwin += TW
        iwin += 1

    print 'Done', ddir
    os.chdir(topdir)

#    if 'jc181' not in ddir:
#    break

if not LOAD:

    mcrates = np.array(mcrates)
    mtrates = np.array(mtrates)
    mcrates /= 21
    mtrates /= 21
    np.savetxt(cpath, mcrates, fmt = '%.4f')
    np.savetxt(tpath, mtrates, fmt = '%.4f')

    allmcrates = np.array(allmcrates)
    allmtrates = np.array(allmtrates)
    np.save(cpath + '.all', allmcrates)
    np.save(tpath + '.all', allmtrates)

LFS = 25
plt.plot(mcrates, linewidth = 4, color='b')
plt.plot(mtrates, linewidth = 4, color='r')
plt.fill_between(range(16), mcrates - cstds, mcrates + cstds, color='b', alpha = 0.3)
plt.fill_between(range(16), mtrates - tstds, mtrates + tstds, color='r', alpha = 0.3)
plt.ylim([0, 1.2 * max(list(mcrates) + list(mtrates))])
plt.gca().locator_params(nbins=5, axis='y')

plt.xticks([3,7,11,15], ['1', '2', '3', '4'])
set_xticks_font(LFS)
set_yticks_font(LFS)

plt.xlabel('Time, h', fontsize = LFS)
plt.ylabel('Mean firing rate, Hz', fontsize = LFS)
plt.legend(['Control', 'Target'])
strip_axes(plt.gca())
plt.tight_layout()

plt.show()
