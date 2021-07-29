#!/usr/bin/env python3

from sys import argv
import numpy as np
import os, glob

if len(argv) < 2:
	print('USAGE: (1)<directory with res files>')
	exit(0)

dr = argv[1]
os.chdir(dr)

for file in glob.glob("*.res.*") + glob.glob('*.res'):
    print('Fix', file)
    res = np.loadtxt(file, dtype=int)
    res *= 6
    res = np.round(res/5)
    np.savetxt(file, res, fmt='%d')
