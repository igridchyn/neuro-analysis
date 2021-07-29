#!/usr/bin/env python

from matplotlib import pyplot as plt
import numpy as np
from numpy import sqrt
from sys import argv
from tracking_processing import whl_to_pos, whl_to_speed

if len(argv) < 6:
	print 'USAGE: (1)<whl file> (2)<res file> (3)<min occ> (4)<min speed> (5)<session (only for plot label)>'
	print 'MEAN TOTAL FIRING RATE IN WINDOW'

whl = whl_to_pos(open(argv[1]), False)
speed = whl_to_speed(whl)
res = [int(r) for r in open(argv[2]) if len(r) > 0]

binsx = 75
binsy = 40

occ = np.zeros((binsy, binsx))
spks = np.zeros((binsy, binsx))

WIN = 2400
time = res[0]
i = 0
SBIN = 4
MINSPEED = float(argv[4])

while i < len(res):
	nspikes = 0
	while i < len(res) and res[i] < time + WIN:
		nspikes += 1
		i += 1
	
	x = round(whl[time / 480][0] / SBIN)
	y = round(whl[time / 480][1] / SBIN)

	if x < 200 and speed[time / 480] > MINSPEED:
		occ[y,x] += 1
		spks[y,x] += nspikes

	time += WIN

MINOCC = int(argv[3])
occ[occ < MINOCC] = 0

plt.imshow(spks / occ, interpolation='none')
plt.colorbar()
plt.title('Mean number of spikes in %d window with speed threshold\n %d and minimal occupancy %d, session = %s' % (WIN, MINSPEED, MINOCC, argv[5]))
plt.show()
