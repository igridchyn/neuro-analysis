#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 4:
	print 'USAGE: (1)<input - event timestamps> (2)<frequency measurement interval, s> (3)<output - frequency file>'
	exit(0)

evt = np.loadtxt(argv[1])[:, 0]
print len(evt)

intvl = float(argv[2]) * 24000
fo = open(argv[3], 'w')

tend = intvl
ecount = 0

i = 0
while i < len(evt):
    if evt[i] < tend:
        ecount += 1
        i += 1
    else:
        fo.write('%.2f' % (ecount * 24000 / intvl) + '\n')
        ecount = 0
        tend += intvl
