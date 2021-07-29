#!/usr/bin/env python

from matplotlib import pyplot as plt
from sys import argv
import numpy as np
from scipy.ndimage.morphology import *

if len(argv) < 10:
	print 'Usage: ' + argv[0] + '(1)<whl file> (2)<nbinsx> (3)<nbinsy> (4)<bin size> (5)<occupancy threshold> (6)<invert: 0/1> (7)<output mat file name> (8)<whl fomat : l/s> (9)<unk value>'
	print 'Generate binary occupancy map for given whl and threshold (e.g. to be used for trigger decision making)'
	exit(0)

whlf = argv[8]
unkval = float(argv[9])

if whlf not in ['l', 's']:
	print '8-th argument (whl format) must be s(short) or l(long)'
	exit(1)

# TODO: speed threshold
whl = []
for line in open(argv[1]):
	parts = line.split(' ')
	if len(line) < 2:
		continue

	if whlf == 's':
		whl.append([float(parts[0]), float(parts[1])])
	else:
		xs = float(parts[0])
		ys = float(parts[1])
		xb = float(parts[2])
		yb = float(parts[3])
		if xs == unkval and xb == unkval:
			continue
		if xs != unkval and xb != unkval:
			whl.append([(xs + xb) / 2, (ys + yb) / 2])
		else:
			if xs == unkval:
				whl.append([xb, yb])
			else:
				whl.append([xs, ys])

nbinsx = int(argv[2])
nbinsy = int(argv[3])
binsize = float(argv[4])
occthold = int(argv[5])
invert = int(argv[6])
occ = np.zeros((nbinsy, nbinsx))
outpath = argv[7]

for pos in whl:
	x = pos[0]
	y = pos[1]
	bx = round(x / binsize)
	by = round(y / binsize)

	if bx >= nbinsx or bx <= 0 or by >= nbinsy or by < 0:
		continue

	occ[by, bx] += 1

plt.imshow(occ, interpolation='none')
plt.colorbar()
plt.show()

occbmap = occ > occthold
# close
occbmap = binary_closing(occbmap)

plt.imshow(occbmap, interpolation='none')
plt.show()

print 'Values >= threshold: %d, values < threshold %d' % (sum(sum(occbmap > 0)), sum(sum(occbmap == 0)))

np.savetxt(outpath, occbmap, fmt = '%d')
