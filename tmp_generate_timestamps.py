#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 2:
	print 'USAGE: (1)<output>'
	exit(0)

fo = open(argv[1], 'w')

#for i in range(120):
#    fo.write(str(24000 * 60 * i) + '\n')

for i in range(12):
    fo.write(str(24000 * 600 * i) + '\n')
