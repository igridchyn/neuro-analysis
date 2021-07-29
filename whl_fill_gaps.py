#!/usr/bin/env python
from sys import argv
from matplotlib import pyplot as plt
import random

class Gap:
	def __init__(self, start, length):
		self.s = start
		self.l = length

f = open(argv[1])
gapmin = int(argv[2])

whl = []

for line in f:
	parts = line[:-1].split(' ')
	whl.append([float(w) for w in parts])

whlg = whl[:]

# find gaps
gapls = []

gap = False
gapl = 0
i = 0
dx = 20.15
dy = 22.63
for w in whl:
	if w[0] > 1000 :
		if  not gap:
			gapl = 0
			gap = True
		else:
			gapl += 1
	else:
		if gapl > 0:
			gapls.append(Gap(i-gapl, gapl))
			gapl = 0
	i += 1

# find runs horizontal environment
runsh = []
i = 0
run = False
runl = 0
runlmin = 150
for w in whl:
	x = w[0]
	y = w[1]
	if x < 120 + dx and x > 120:
		if not run:
			if y > 70:
				run = True
				runl = 0
		else:
			runl += 1
	else:
		if run:
			if runl > runlmin:
				runsh.append(Gap(i - runl, runl))
			run = False
			runl = 0

	i += 1

gaplens = [g.l for g in gapls if g.l > gapmin]
gapstartsx = [whl[g.s][0] for g in gapls if g.l > gapmin]
gapstarts = [g.s for g in gapls if g.l > gapmin]

print 'Total gaps: %d' % len(gaplens)

plt.hist(gaplens)
plt.show()
plt.hist(gapstartsx)
plt.show()

print 'Number of runs horizontal: %d' % len(runsh) 

# generate mark where the gap occurred
for i in range(0, len(gaplens)):
	whlg[gapstarts[i]][0] = whlg[gapstarts[i] - 1][0] - 10 + 5*random.random()
	whlg[gapstarts[i]][1] = whlg[gapstarts[i] - 1][1] - 10 + 5*random.random()

# save whl
fo = open(argv[1] + '.gen', 'w')
for w in whlg:
	for c in w[0:4]:
		fo.write(str(c) + ' ')
	fo.write(str(int(w[4])) + ' ')
	fo.write(str(int(w[5])) + '\n')
