#!/usr/bin/env python

# analyze evolution of confidence in the synchorny events in sleep : from dump and log files

from matplotlib import pyplot as plt
import numpy as np
from sys import argv
from imath import gaussian

f = open(argv[1])

confs = []
for line in f:
	confs.append(float(line))

gs = gaussian(200, 100)

confs = np.convolve(confs, gs)

plt.plot(confs)
plt.grid()
plt.show()
