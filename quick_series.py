#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats

if len(argv) < 4:
	print('USAGE: (1)<file with list of dirs - series> (2)<filename to lookd for in dir> (3)<series cut length>')
	exit(0)

if len(argv) > 4:
    pdic = parse_optional_params(argv[4:])

slen = int(argv[3])

if argv[1] != '-':
    for line in open(argv[1]):
        if 'ser' in locals():
            ser = np.vstack((ser, np.loadtxt(line[:-1] + '/' + argv[2])[:slen]))
        else:
            ser = np.loadtxt(line[:-1] + '/' + argv[2])[:slen]
else:
    ser = np.loadtxt(argv[2])
    ser = ser.reshape((-1, slen))

n = ser.shape[0]
mean = np.mean(ser, axis = 0)        
sem = np.std(ser, axis = 0) / np.sqrt(n)

fig, ax = plt.subplots()
x = range(ser.shape[1])
ax.plot(x, mean)
ax.fill_between(x, mean-sem, mean+sem, alpha=0.2)

LFS = 20
if 'xl' in pdic: plt.xlabel(pdic['xl'], fontsize=LFS)
if 'yl' in pdic: plt.ylabel(pdic['yl'], fontsize=LFS)
if 'ti' in pdic: plt.title(pdic['ti'], fontsize=LFS)

strip_axes(ax)
plt.tight_layout()

plt.show()
