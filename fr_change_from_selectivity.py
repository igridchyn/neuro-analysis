#!/usr/bin/env python

# analyze change in FR as a function of selectivity

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
from math import log

if len(argv) < 4:
	print 'USAGE: (1)<firing rates 1> (2)<firing rates 2> (3)<PFS dump>'
	exit(0)

fr1 = [float(f) for f in open(argv[1])]
fr2 = [float(f) for f in open(argv[2])]

fr1 = fr1[1:]
fr2 = fr2[1:]

pfr1 = []
pfr2 = []

for line in open(argv[3]):
	ws = line.split(' ')
	pfr1.append(float(ws[3]))
	pfr2.append(float(ws[4]))

# plt.scatter(fr1, fr2)
MINPFR = 0.5
#frrat = [log(fr2[i] / fr1[i]) if fr1[i] > 0 and fr2[i] > 0 else 0 for i in range(len(fr2))]
frrat = [(fr2[i] - fr1[i])/(fr2[i] + fr1[i]) if fr2[i] > 0 and fr1[1] > 0 else 0 for i in range(len(fr2))]

#sel = [log(pfr2[i] / pfr1[i]) if pfr1[i] > MINPFR and pfr2[i] > MINPFR else 0 for i in range(len(pfr2))]
sel = [(pfr2[i] - pfr1[i])/(pfr2[i] + pfr1[i]) if pfr1[i] > MINPFR and pfr2[i] > MINPFR else 0 for i in range(len(pfr2))]

frrat = np.array(frrat)
sel = np.array(sel)

# 2X => 0.69
idx = (frrat != 0) & (sel != 0) & (abs(sel) > 0.1)

print np.corrcoef(sel[idx], frrat[idx])[0, 1]

plt.scatter(sel[idx], frrat[idx])
plt.show()
