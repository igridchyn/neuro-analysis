#!/usr/bin/env python

import os
import glob
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from numpy import log, exp

m1 = np.load(argv[1])
m2 = np.load(argv[2])

diff = m1 - m2
# diff = np.transpose(diff)

plt.figure()
plt.imshow(diff, interpolation = 'none')
plt.colorbar(orientation = 'horizontal')
plt.show()
