#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from scipy import stats

if len(argv) < 4:
	print('USAGE: (1)<file with sessions> (2)<file with pyr ids, placeholder SESSION> (3)<output>')
	exit(0)

sessions = [s.strip() for s in open(argv[1]).readlines()]
pyrid = np.loadtxt(argv[2], dtype=int)
pfs_gname = 'pfs_SESSION.txt'

fout = open(argv[3], 'w')

for i in range(len(sessions)):
	pfss = np.loadtxt(pfs_gname.replace('SESSION', sessions[i]))
	pfs = pfss[pyrid[i]]
	fout.write('%.5f\n' % (-2 if np.isnan(pfs) else pfs))
