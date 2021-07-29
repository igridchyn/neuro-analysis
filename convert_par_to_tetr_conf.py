#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats

if len(argv) < 2:
	print('USAGE: (1)<template.par> (2)<conf out>')
	exit(0)

f = open(argv[1])
f.readline()
f.readline()
f.readline()

tetchans = f.readlines()

ftc = open(argv[2], 'w')
ftc.write('%d\n' % len(tetchans))
for i in range(len(tetchans)):
    ftc.write(tetchans[i][0] + '\n')
    ftc.write(tetchans[i][2:])
