#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *
import struct

if len(argv) < 3:
    print 'USAGE: (1)<fet file base> (2)<tetrode config>'
    exit(0)

BASE = argv[1]

# read tetrode config
ft = open(argv[2])
ntet = int(ft.readline())
PCNS = []
for i in range(ntet):
        PCNS.append(int(ft.readline()) * 2)
        ft.readline()
print 'Numbers of channels per tetrode:', PCNS

tetr = 0
while os.path.isfile(BASE + str(tetr)):
   
    fo = open(BASE.replace('fetb', 'fet') + str(tetr), 'w')

    PCN = PCNS[tetr]
    fo.write('%d\n' % (PCN + 5))

    FETN = PCNS[tetr] + 4
    fmt = FETN * 'f' + 'i'
    struct_size = 4 * (FETN + 1)

    f = open(BASE+str(tetr))
    
    while True:
        spikebin = f.read(struct_size)

        if not spikebin:
            break
        
        fet = struct.unpack(fmt, spikebin)
        # write multiplied X50 and rounded features:
        fo.write(PCN*'%d ' % tuple([int(fe*50) for fe in fet[:PCN]]))
        fo.write((5*'%d ' + '\n') % tuple([int(fe) for fe in fet[PCN: PCN+5]]))
    
    fo.close()
    tetr += 1

    print 'Done tetrode %d/%d' % (tetr, ntet)

print 'Done, file %s does not exist' % (BASE + str(tetr))
