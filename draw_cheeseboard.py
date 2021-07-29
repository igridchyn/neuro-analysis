#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

if len(argv) < 1:
	print 'USAGE: (1)<> (2)<> (3)<>'
	exit(0)

plt.figure(figsize=(10,10))
#circle = plt.Circle((0, 0), 0.5, color='black', fill=False)

#plt.clf()
plt.axis('off')
ax = plt.gca()

rad = 0.25
for i in range(5):
	for j in range(2-i, 7+i):
		circle = plt.Circle((i, j), rad, color='black', fill=False, linewidth=3)
		ax.add_artist(circle)

for i in range(1,4):
	for j in [1-i, 7+i]:
		circle = plt.Circle((i, j), rad, color='black', fill=False, linewidth=3)
		ax.add_artist(circle)

for i in range(5):
	for j in range(-3, 12):
		circle = plt.Circle((5+i, j), rad, color='black', fill=False, linewidth=3)
		ax.add_artist(circle)

for i in range(5):
	for j in range(-2+i, 11-i):
		circle = plt.Circle((10+i, j), rad, color='black', fill=False, linewidth=3)
		ax.add_artist(circle)

for i in range(1,4):
	for j in [-3+i, 11-i]:
		circle = plt.Circle((10+i, j), rad, color='black', fill=False, linewidth=3)
		ax.add_artist(circle)

circle = plt.Circle((7,4), 7.9, color='black', fill=False, linewidth=3)
ax.add_artist(circle)

plt.ylim(-5, 13)
plt.xlim(-1, 17)
plt.show()
