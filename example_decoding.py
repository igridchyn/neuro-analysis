#!/usr/bin/env python
# plot real trajectory and decoded one - from the dec_bay.txt output of the lfpo

import numpy as np
from sys import argv
from matplotlib import pyplot as plt
from call_log import *

if len(argv) < 2:
	print 'USAGE: (1)<lfp_online output - dec_bay.txt>'
	exit(0)

log_call(argv)

f = open(argv[1])
f.readline()
f.readline()

pos_real = []
pos_dec = []

lfs = 20

for line in f:
	ws = [float(f) for f in line.split(' ')]
	if ws[3] < 1000:
		pos_real.append(ws[2])
		pos_dec.append(ws[0])
plt.figure(figsize=(6,5))
time = np.arange(len(pos_real)) / 1.75
plt.plot(time, pos_real)
plt.scatter(time, pos_dec, color = 'r')
plt.legend(['Real', 'Decoded'], loc='best')
plt.xlabel('Time, s', fontsize=lfs)
#plt.ylabel('Position')
#plt.xticks([],[])

#plt.yticks([],[])
#plt.yticks([25, 145, 220, 335],['START\nBOX 1', 'GOAL 1', 'START\nBOX 2', 'GOAL 2'])
plt.yticks([145, 25, 335, 220],['START\nBOX 1', 'GOAL 1', 'START\nBOX 2', 'GOAL 2'])
plt.axhline(y=25, color='green')
plt.axhline(y=145, color='green')
plt.axhline(y=220, color='green')
plt.axhline(y=335, color='green')
plt.ylim([0, 350])

ax2 = plt.gca().twinx()
ax2.set_ylabel('Linearised position, cm', fontsize = lfs)
tr = np.arange(0, 1.1, 0.2)
#ax2.set_yticks(tr, [0, 60, 120, 0, 60, 120])
ax2.set_yticklabels([0, 60, 120, 0, 60, 120])

plt.tight_layout()
plt.show()
