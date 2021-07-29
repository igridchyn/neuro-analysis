#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
import struct

if len(argv) < 4:
	print 'USAGE: (1)<filtered channel> (2)<time interval, s> (3)<output file>'
	exit(0)

f = open(argv[1], 'rb')
intvl = int(float(argv[2]) * 24000)
outpath = argv[3]
avgpow = []
repint = 24000 * 60 * 5

eof = False
while not eof:
    dat = f.read(intvl * 2)
    sig = struct.unpack('%dh' % (len(dat)/2), dat)

    avgpow.append(np.sqrt(np.mean([s**2 for s in sig])))

    eof = len(dat) < intvl * 2

avgpow = np.array(avgpow)

np.savetxt(outpath, avgpow)
