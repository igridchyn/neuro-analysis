#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

if len(argv) < 1:
	print 'USAGE: (1)<palce field prefix>'
	exit(0)

# load place fields, rotate, compare, average

pfbase = argv[1]
c = 0

# [gx1, gy1, gx2, gy2, tana]

while os.path.isfile(pfbase + str(c) + '_2.mat'):
    pf = np.loadtxt()

    # caculate rotaiton of TARGET vs. CONTROL - ALIGN the start box !
    
    # find out angle - from SB and GOAL locations

    # calulcate PFS ...

# use values generated with R
plt.bar([0], vals[0], width=0.3)
plt.bar([1], vals[1], width=0.3)
plt.legend(['Same environment', 'Different environments'], fontsize=15)
plt.errorbar([0, 1], vals, yerr=stds, fmt='.', color = 'black')
LFS = 15
plt.xticks([])
plt.ylabel('Place field similarity, r', fontsize = LFS+10)
plt.title('Comparison of control and target maps\ntrials 8-9 vs. trials 10-11', fontsize=20)
plt.xlim(-0.5, 1.5)
plt.yticks([0.0, 0.25, 0.5, 0.75])
set_yticks_font(20)
strip_axes(plt.gca())
plt.tight_layout()
plt.show()
