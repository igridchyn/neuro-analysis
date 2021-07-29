#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 2:
	print 'USAGE: (1)<file with session couple and fractions'
	exit(0)

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

rattab = np.loadtxt(argv[1])

ses1 = []
ses2 = []

sesnames = ['', '1st learning trial', 'End of learning', 'Probe', '1st post-learning trial', 'End of post-learning']

for i in range(len(rattab)):
    ses1.append(int(rattab[i,0]))
    ses2.append(int(rattab[i,1]))

# plot long bar chart : 3X2 

labs = []
plt.figure(figsize = (19, 6))

for i in range(len(rattab)):
    xb = np.array([1,2, 4,5, 7,8]) + 15 * i
    plt.bar(xb, [rattab[i,2], rattab[i,5], rattab[i,3], rattab[i,6], rattab[i,4], rattab[i,7]], color=['b', 'r', 'b', 'r', 'b', 'r'])
    labs.append(sesnames[ses1[i]] + ' vs.\n' + sesnames[ses2[i]])

    tholdar = [0.4, 0.5, 0.6]
    for j in range(3):
        plt.text(xb[2*j], 0.75, '%.1f' % tholdar[j], fontsize=15)

plt.ylim([0, 0.76])
# plt.xlim([0, (len(rattab) - 1) * 15])

plt.ylabel('Fraction of PFS < threshold', fontsize = 20)
plt.xticks(range(5, 15 * len(rattab), 15), labs)
set_xticks_font(20)
set_yticks_font(20)
strip_axes(plt.gca())
plt.gca().locator_params(nbins=5, axis='y')
plt.tight_layout()

plt.show()
