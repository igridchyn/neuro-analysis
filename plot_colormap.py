#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt
from tracking_processing import whl_to_pos, whl_to_speed
from sys import argv
from math import atan2, cos, sin, sqrt

if len(argv) < 2:
	print 'Usage: (1)<LFPO dump in format [value x y speed]>'
	print 'Plot color map of value, filtered by speed + distribution of (value, speed) - created to visualize head direction variance'
	exit(0)

f = open(argv[1])

vals = []
xs = []
ys = []
sp = []
for line in f:
	w = line.split(' ')
	if len(w) < 3:
		continue

	vals.append(float(w[0]))
	xs.append(float(w[1]))
	ys.append(float(w[2]))
	sp.append(float(w[3]))

BIN = 4
NBX = 80
NBY = 45

mp = np.zeros((NBX, NBY))
mpo = np.zeros((NBX, NBY))

for i in range(len(xs)):
	# print xs[i]

	bx = xs[i] / BIN
	by = ys[i] / BIN

	mp[bx, by] += 1 - vals[i]
	mpo[bx, by] += 1

#plt.figure()
f, axarr = plt.subplots(2)
im1 = axarr[0].imshow(mp / mpo, interpolation = 'none')
f.colorbar(im1)

BINP = 0.05
BINS = 0.75
NB = 20
spvsmp = np.zeros((NB, NB))
for i in range(len(sp)):
	bs = sp[i] / BINS
	bp = vals[i] / BINP
	if bs < 0 or bs >= NB or bp < 0 or bp >= NB:
		continue
	spvsmp[bs, bp] += 1

#plt.figure()
spvsmp[0:5, 0:5] = 0
im = axarr[1].imshow(spvsmp, interpolation = 'none')
f.colorbar(im)

plt.show()
