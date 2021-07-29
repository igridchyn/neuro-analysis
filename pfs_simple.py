#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from scipy import stats

if len(argv) < 4:
	print('USAGE: (1)<base 1 w CELL_ID placeholder> (2)<base 2 w CELL_ID placeholder> (3)<output>')
	exit(0)

BASE1 = argv[1]
BASE2 = argv[2]
FOUT = open(argv[3], 'w')

clu = 0
while os.path.isfile(BASE1.replace('CELL_ID', str(clu))):
	rm1 = np.loadtxt(BASE1.replace('CELL_ID', str(clu)))
	rm2 = np.loadtxt(BASE2.replace('CELL_ID', str(clu)))

	rm1 = rm1.flatten()
	rm2 = rm2.flatten()
	ind = ~np.isnan(rm1) & ~ np.isnan(rm2)

	pfs = np.ma.corrcoef(rm1[ind], rm2[ind])[0,1]
	FOUT.write('%.5f\n' % pfs)

	clu += 1
