#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
#from call_log import *
from scipy import stats
from collections import deque
import struct

if len(argv) < 5:
	print('USAGE: (1)<dat file> (2)<rotation start sample> (3)<total number of channels> (4)<output file>')
	exit(0)

path = argv[1]
t = int(argv[2])
nchan = int(argv[3])
opath = argv[4]

f = open(path, 'rb')
fo = open(opath, 'wb')

# copy before timestamp
#f.seek(nchan * 2 * t)
head = f.read(nchan * 2 * t)
fo.write(head)

# read samplle-by-sample and rotate; if too slow - read in batches
while True:
    batch = f.read(2 * nchan)
    datar = struct.unpack('%dh' % nchan, batch)

    if len(datar) < 34:
        print('Read %d numbers, exit' % len(datar))
        break

    d = deque(datar)
    d.rotate(-16)
    rot_ar = list(d)
    #print(rot_ar)

    fo.write(struct.pack('%dh' % nchan, *rot_ar))
