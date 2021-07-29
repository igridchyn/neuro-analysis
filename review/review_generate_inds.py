#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 1:
	print 'USAGE: (1)<list of directories> (2)<file name>'
	exit(0)

# TO GET THE NUMBER OF CELLS: USE length of the 'coherence_BS6_OT5.txt' - in day directory

ainds = []

for dr in open(argv[1]):
    dr = dr.strip()

    cohs = np.loadtxt(dr + '/coherence_BS6_OT5_E1.txt')
    ncell = len(cohs)

    inds = [False] * (ncell + 1)

    iinds = np.loadtxt(dr + '/ints.txt', dtype=int)

    if iinds.ndim == 0:
        iinds = np.array([iinds])

    for ii in iinds:
        inds[ii] = True

    ainds.extend(inds)

np.savetxt('int_inds.txt', ainds)
