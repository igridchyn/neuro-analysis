#!/usr/bin/env python

from sys import argv
import numpy as np
from iutils import *

if len(argv) < 4:
	print 'USAGE: (1)<res/clu basename> (2)<timestamps file> (3)<out path>'
	exit(0)

argv = resolve_vars(argv)

rcbase = argv[1]
intpath = argv[2]
outpath = argv[3]

res = []
clu = []
for line in open(rcbase + 'res'):
        res.append(int(line))
for line in open(rcbase + 'clu'):
        clu.append(int(line) - 1)
print 'Length of clu/res: %d / %d' % (len(clu), len(res))
NC = max(clu) + 1

# load intervals for light effect quantification
wins = []
WIN = 2400
print 'WARINING: fixed window around timestamp =', WIN
for line in open(intpath):
        #vals = [int(i) for i in line.split(' ')]
	val = int(line)
	vals = [val - WIN, val, val + WIN]
        wins.append(vals)

# calculate mean firing rates of all cells - in windows before and after
# (count total spikes in windows before and after)
iwin = 0
ires = 0

# rate arrays - before and after
ratesa = [0] * NC
ratesb = [0] * NC

# lists of event-wise firing rates (optionally, Z-scored)
rateslista = [[] for i in range(NC)]
rateslistb = [[] for i in range(NC)]

# post-accounting delay
PADEL = 0

while ires < len(res) and iwin < len(wins):
        # find first spikes in the before-window
        while ires < len(res) and res[ires] < wins[iwin][0]:
                ires += 1

        popvec = [0] * NC
        # calculate before-popvec
        while ires < len(res) and res[ires] < wins[iwin][1]:
                popvec[clu[ires]] += 1
                ires += 1

        # update average firing rates
        time = (wins[iwin][1] - wins[iwin][0]) / 24000.0
        for c in range(NC):
                ratesb[c] += popvec[c] / time
                rateslistb[c].append(popvec[c]) # / time)

        # introduce delay after the light before accounting spikes
        while ires  < len(res) and res[ires] < wins[iwin][1] + PADEL:
                ires += 1

        # calculate after-popvec
        popvec = [0] * NC
        while ires < len(res) and res[ires] < wins[iwin][2] + PADEL:
                popvec[clu[ires]] += 1
                ires += 1
        time = (wins[iwin][2] - wins[iwin][1]) / 24000.0
        for c in range(NC):
                ratesa[c] += popvec[c] / time
                rateslista[c].append(popvec[c]) # / time)

        iwin += 1

arateslista = np.array(rateslista)
arateslistb = np.array(rateslistb)
corrsa = np.corrcoef(arateslista)
corrsb = np.corrcoef(arateslistb)
np.save(outpath + '.corrmats', [corrsb, corrsa])
