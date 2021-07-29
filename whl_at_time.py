#!/usr/bin/env python3

from sys import argv
from matplotlib import pyplot as plt
import numpy as np

def whl_to_pos(w):
	if w[0] < 1000 and w[2] < 1000:
		return (w[0] + w[2]) / 2.0, (w[1] + w[3]) / 2.0
	
	if w[0] < 1000:
		return w[0], w[1]

	if w[2] < 1000:
		return w[2], w[3]

	return 1024, 1024
		
if len(argv) < 3:
	print('Usage: (1)<whl file> (2)<timestamps file>')

#ldir = log_call(argv)

whl = []
for line in open(argv[1]):
	if len(line) == 0:
		continue

	fs = [ float(a) for a in line.split(' ') ]
	whl.append(fs)

print('Read %d whl entries' % len(whl))
print('Last time = %.2f' % whl[-1][-2])

tts = [int(t) for t in open(argv[2])]

print('Read %d timestamps' % len(tts))

i = 0
# trigger locations
xtr = []
ytr = []
for tt in tts:
	# advance to first > timestamp
	while i < len(whl) and whl[i][-2] < tt:
		i += 1	

	x = 1024
	y = 1024
	# get first known pos
	while i < len(whl) and x == 1024:
		x,y = whl_to_pos(whl[i])
		i += 1

	xtr.append(x)
	ytr.append(y)

# plt.scatter(xtr, ytr)
# plt.scatter([a[0] for a in whl], [a[1] for a in whl])
# plt.show()

# binned occupancy
bin = 8
pos = [whl_to_pos(w) for w in whl]

nbinsx = max([p[0] for p in pos if p[0] < 1000]) / bin + 1
nbinsy = max([p[1] for p in pos if p[1] < 1000]) / bin + 1

print('Number of bins: %d / %d' % (nbinsx, nbinsy))

# trigger map
tmap = np.zeros((nbinsx, nbinsy))
for i in range(len(xtr)):
	bx = xtr[i] / bin
	by = ytr[i] / bin
	tmap[bx, by] += 1

omap = np.zeros((nbinsx, nbinsy))
for p in pos:
	if p[0] < 1000:
		bx = p[0] / bin
		by = p[1] / bin
		omap[bx, by] += 1

tfreq = tmap / omap
occthold = 10
tfreq[omap < occthold] = 0

fig, ax = plt.subplots()
plt.imshow(tfreq, interpolation='none')
plt.show()
#fig.savefig(ldir + 'trig_map.png')
