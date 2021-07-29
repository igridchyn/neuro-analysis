#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

if len(argv) < 2:
	print 'USAGE: (1)<decoder output>'
	exit(0)

xrs = []
xps = []

DSC = 2

for line in open(argv[1]):
	ws = line.split(' ')
	if len(ws) < 6:
		continue

	# real / predicted
	xr = int(round(float(ws[2])))
	xp = int(ws[0])

	if xr > 1000:
		continue

	xrs.append(xr / DSC)
	xps.append(xp / DSC)

md = max(len(xrs), len(xps)) + 1
confm = np.zeros((md, md))

for i in range(len(xrs)):
	confm[xrs[i], xps[i]] += 1

plt.figure(figsize=(10,10))

confm = np.max(confm) - confm
ind = np.hstack((np.arange(0,150/DSC), np.arange(210/DSC,350/DSC)))
plt.imshow(confm[ind, :][:, ind], interpolation='nearest', cmap='gray')
plt.axvline(x=150/DSC)
plt.axhline(y=150/DSC)

set_xticks_font(20)
set_yticks_font(20)

#plt.tight_layout()
plt.subplots_adjust(bottom=0.09, left=0.12, top=0.96, right=0.99)

LFS = 30
plt.xlabel('Position', fontsize=LFS)
plt.ylabel('Reconstructed position', fontsize=LFS)
plt.show()
