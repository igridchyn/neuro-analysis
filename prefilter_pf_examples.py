#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

if len(argv) < 4:
	print 'USAGE: (1)<PFS suffix> (2)<PFs directory> (3)<list of animal/day directories>'
	exit(0)

pfssuf = argv[1]
pfsdir = argv[2]
dirspath = argv[3]

for line in open(dirspath):
	dr = line[:-1]
	print 'Directory:', dr
	if len(dr) < 2:
		break

	hdir = os.getcwd()
	os.chdir(dr)

	pfs23 = read_float_array(pfssuf % (2, 3))
	pfs24 = read_float_array(pfssuf % (2, 4))
	pfs25 = read_float_array(pfssuf % (2, 5))

	[animal, day, swap, full] = resolve_vars(['%{animal}', '%{day}', '%{swap}', '%{FULL}'])
	swap = int(swap)

 	# 0.4/0.3  COND1	
	# 0.5/0.25 COND2
	MINCONPFS = 0.4
	MAXTARGPFS = 0.3
	exind = (pfs23[:, 2-swap] > MINCONPFS) & (pfs24[:, 2-swap,] > MINCONPFS) & (pfs23[:, 1+swap] < MAXTARGPFS) & (pfs24[:, 1+swap] < MAXTARGPFS)
	nc = pfs23.shape[0]
	print nc, 'cells', np.sum(exind), 'pass'

	os.chdir(('9f%s/' % full) + pfsdir)
	for c in range(nc):
		if exind[c]:
			# run example generation + save
			os.system('python /home/igor/bin/plot_place_field.py pf_%d_2.mat' % (c+1))

	os.chdir(hdir)
