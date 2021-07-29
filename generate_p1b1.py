#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

if len(argv) < 3:
	print 'USAGE: (1)<basename> (2)<cutoff freuqncy, Hz>'
	exit(0)

BASE = argv[1]
CUTOFF_HZ = float(argv[2])

clu = read_int_list(BASE + 'clu')
res = read_int_list(BASE + 'res')
dursec = res[-1] / 24000.0

nclu = max(clu)

fp1 = open('list.p1', 'w')
fb1 = open('list.b1', 'w')
fdes = open(BASE + 'des', 'w')

for c in range(1, nclu + 1):
    fr_c = clu.count(c) / dursec
    if fr_c > CUTOFF_HZ:
        fb1.write('%d\n' % c)
        fdes.write('%s\n' % 'b1')
    else:
        fp1.write('%d\n' % c)
        fdes.write('%s\n' % 'p1')

fb1.close()
fp1.close()
