#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 3:
	print 'USAGE: (1)<dir list> (2)<fiel name>'
	exit(0)

fname = argv[2]

tholdyn = []

for d in open(argv[1]):
    thold = np.loadtxt(d.strip() + '/' + fname)

    print tholdyn

    # find swap
    for line in open(d.strip() + '/../about.txt'):
        if line.startswith('swap'):
            swap = bool(int(line[-2]))
            print swap
            break

    # standardize and reverse if need
    thold = (thold - np.mean(thold)) / np.std(thold)
    if swap:
        thold = - thold

    if len(tholdyn) == 0:
        tholdyn = thold
    else:
        # cut to fit
        if len(tholdyn) > len(thold):
            tholdyn = tholdyn[:len(thold)]
        else:
            thold = thold[:len(tholdyn)]
        tholdyn += thold

LFS = 20
plt.plot(range(3, len(tholdyn)*3+3, 3), tholdyn, linewidth=5)
plt.xlabel('Sleep time, min', fontsize=LFS)
plt.ylabel('Trigger threshold, z', fontsize=LFS)
ax = plt.gca()
# remove top and right spines - frame axes
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.show()
