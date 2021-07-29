#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
from tracking_processing import *

if len(argv) < 5:
	print 'USAGE: (1)<base for place fields> ()<place fields session> ()<trajectory> (4)<output base for clu/res>'
        print 'Simulate firing according to given map on the trajectory of the other map'
	exit(0)


pfbase = argv[1]
session = argv[2]
whl =  whl_to_pos(open(argv[3]), False)
outbase = argv[4]

# don't mind spee here - it will be ignored if necessary during subsequent place field construction ...

# whl sampling rate is 480

pfs = []
c = 1
pfpath = '%s%s_%s.mat' % (pfbase, c, session)
print pfpath
while os.path.isfile(pfpath):
    pfs.append(np.loadtxt(pfpath))
    c += 1
    pfpath = '%s%s_%s.mat' % (pfbase, c, session)

print '% d cells loaded, size:' % c, pfs[0].shape

clu = []
res = []

BS=6
for iw in range(len(whl)):
    pos = whl[iw]
    # for every cell - consider 480 interval and generate spikes

    for c in range(len(pfs)):
        xb = int((pos[0]/BS)) # round ?
        yb = int((pos[1]/BS)) # round ?
        rate = pfs[c][yb, xb]

        if np.isnan(rate) or np.isinf(rate) or rate < 0.00001:
            continue

        prob = rate # NO NEED TO SCALE IF LFPO-BASED FIELDS !!! - already have rates for 20 ms periods ...

        # generate how many spikes
        # print prob
        nsp = np.random.poisson(prob)
        for i in range(nsp):
            clu.append(c + 1)
            res.append(iw * 480 + i * 50)

clu = np.array(clu)
res = np.array(res)
isort = np.argsort(res)
res = res[isort]
clu = clu[isort]

np.savetxt(outbase + 'clu', clu, fmt='%d') 
np.savetxt(outbase + 'res', res, fmt='%d') 
