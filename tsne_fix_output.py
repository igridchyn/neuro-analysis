#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

# fix the output of the tsne script by removing 3 columns of the 3d tsne and replacing the 3rd and 4th (extra) features with the 2d tsne

if len(argv) < 3:
	print 'USAGE: (1)<input - tsne output> (2)<output - fixed tsne output>'
	exit(0)

f = open(argv[1])
fo = open(argv[2], 'w')

sclun = f.readline()

# can be 19-17-15 corresponding to 4-3-2 channels, 2 PC each
clun = int(sclun)

fo.write(str(clun-5) + '\n')

for line in f:
    ws = line.split(' ')

    # wrtie as:  PC features + 2 extra features + 2 tsne features + time (once or twice, need to figure out - depends on back - conversion)
    # normal FET is for 4 channels: 8 PC + 4 extra + (2X) time
    fo.write(' '.join(ws[:clun-8]) + ' ' + str(int(ws[-4])/10) + ' ' + str(int(ws[-3])/10) + ' ' + ws[-2] + '\n')
