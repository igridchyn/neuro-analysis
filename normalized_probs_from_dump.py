#!/usr/bin/env python

# dump timestamps of the most / least probable (normalized b sum) windows from the SWR deciding dump

from sys import argv
from matplotlib import pyplot as plt
from math import exp
import numpy as np

normprobs1 = []
normprobs2 = []
times = []

curswr = -1
nxt = False

for line in open(argv[1]):
	ws = line.split(' ')
	swri = int(ws[0])
	if swri == curswr:
		continue

	if not nxt:
		nxt = True
		continue	

	nxt = False

	mx1 = float(ws[2])
	mx2 = float(ws[3])
	sm = float(ws[-1])

	t = int(ws[1])

	normprobs1.append(exp(mx1 - sm))
	normprobs2.append(exp(mx2 - sm))
	times.append(t)

	curswr += 1

nps1 = np.array(normprobs1)
nps2 = np.array(normprobs2)

plt.scatter(normprobs1, normprobs2)
plt.show()

times = np.array(times)

fo1 = open(argv[1] + '.high1', 'w')
for t in times[nps1 > 0.5]:
	fo1.write(str(t) + '\n')
fo2 = open(argv[1] + '.high2', 'w')
for t in times[nps2 > 0.5]:
	fo2.write(str(t) + '\n')
