#!/usr/bin/env python2

import struct
from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 4:
    print 'USAGE: (1)<theta filetered signal> (2)<delta filtered signal> (3)<output file: delta-theta ratio>'
    exit(0)

# CALCULATION INTERVAL : 24000 * 60 = 1 MINUTE
writeint = 24000 * 60 # 1.44 M
batch = writeint * 10
varcalcint = 24000

# running window containing 16 samples
lrunar = writeint

runar = lrunar * [0]
irunar = 0
sumrunar = 0

runard = lrunar * [0]
sumrunard = 0

# variability for every second - then take average
varar = [0] * 60

# ratios array
rats = []

ft = open(argv[1], 'rb')
fd = open(argv[2], 'rb')
fo = open(argv[3], 'w')
#fov = open(argv[3] + '.var', 'w')

eof = False
# POWER SCALE ?
PSC = 5000.0

itcount = 0
itrepint = 2

while not eof:
        itcount += 1
        if itcount % itrepint == 0:
            print itcount

        dt = ft.read(2*batch)
        dd = fd.read(2*batch)
        if len(dt) < 2*batch:
                eof = True
                batch = len(dt)
                break
        
        bdatt = struct.unpack('%dh' % batch, dt)
        bdatd = struct.unpack('%dh' % batch, dd)

        for i in range(batch):
            sumrunar -= runar[irunar]
            runar[irunar] = (bdatt[-batch + i] ** 2) / float(lrunar) / PSC
            sumrunar += runar[irunar]

            sumrunard -= runard[irunar]
            runard[irunar] = (bdatd[-batch + i] ** 2) / float(lrunar) / PSC
            sumrunard += runard[irunar]

            irunar = (irunar + 1) % lrunar
    
#            if (i+1) % varcalcint == 0:
#                ivarar = (int((i+1) / varcalcint) - 1) % 60
#                varar[ivarar] = np.std([bdatt[-batch+ii]/bdatd[-batch+ii] for ii in range(i-varcalcint+1,i) if bdatd[-batch+ii] > 0])

            #rats.append(sumrunar / sumrunard)
            if (i+1) % writeint == 0:
                fo.write('%.2f' % (sumrunar / sumrunard) + '\n')
                #fov.write('%.2f\n' % np.mean(varar))
