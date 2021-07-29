#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *
from tracking_processing import distance

if len(argv) < 5:
	print 'USAGE: (1)<PF base> (2)<session before> (3)<session after> (4)<outpath> (5)<compath1 - optional> (5)<compath2 - optional>'
	print 'ANALYZE PF WRT. GOAL LOCATION ...'
	exit(0)

argv = argv + ['%{FULL}']
argv = resolve_vars(argv, True)
log_call(argv)

pfbase = argv[1]
s1 = argv[2]
s2 = argv[3]
outpath = argv[4]

full = argv[-1]

if os.path.isfile(outpath):
	print 'ERROR: output file exists, delete first'
	exit(1)

pfs_1 = []
pfs_2 = []

NC = 1

pf1path = '%s%d_%s.mat' %(pfbase, NC, s1)
pf2path = '%s%d_%s.mat' %(pfbase, NC, s2)
l2_occ_path = '%socc_2.mat' % pfbase
l2_occ = np.genfromtxt(l2_occ_path)

# WORKAROUND
#pf1path = '%spf_%d_%s.mat' %(pfbase, NC, s1)
#pf2path = '%s../../14post%s/pfs_POST_1MIN/pf_%d_%s.mat' %(pfbase, full, NC, s2)

print pf1path

print 'WARNING: assume bin size 6'
BS = 6

# distances from peak to goal
# [control, target]
dist_s1 = [[], []]
dist_s2 = [[], []]
peakfrs_s1 = [[], []]
peakfrs_s2 = [[], []]
d_sbg = [[], []]
# from start box to peak
d_sbp = [[], []]

# peak coords : control / target
pkcr = [[], []]

# USE COM INSTEAD
USECOM = False
if len(argv) > 6:
	compath1 = argv[5]
	compath2 = argv[6]
	fcom1 = open(compath1)
	fcom2 = open(compath2)	
	USECOM = True

while os.path.isfile(pf1path):
	pf1 = np.genfromtxt(pf1path)
	# in case of different batches
	if not os.path.isfile(pf2path):
		pf2 = np.zeros(pf1.shape)
	else:
		pf2 = np.genfromtxt(pf2path)
	
	# needed for max
	pf1[np.isinf(pf1)] = np.nan
	pf2[np.isinf(pf2)] = np.nan

	# use only bins occupied in the 2nd session for comparison
	print 'WARNING: considering only the bins that were traversed in the 2nd half of learning'
	ind_l2_nocc = (l2_occ < 1) | np.isnan(l2_occ) | np.isinf(l2_occ)
	pf1[ind_l2_nocc] = np.nan
	pf2[ind_l2_nocc] = np.nan

	halfx = pf1.shape[1] / 2

	pf1am_e1 = np.nanargmax(pf1[:, :halfx])
	pf1am_e2 = np.nanargmax(pf1[:, halfx:])
	pf2am_e1 = np.nanargmax(pf2[:, :halfx])
	pf2am_e2 = np.nanargmax(pf2[:, halfx:])

	mx1_xb_e1 = pf1am_e1 % halfx
	mx1_yb_e1 = pf1am_e1 / halfx
	mx2_xb_e1 = pf2am_e1 % halfx
	mx2_yb_e1 = pf2am_e1 / halfx
	mx1_xb_e2 = pf1am_e2 % halfx + halfx
	mx1_yb_e2 = pf1am_e2 / halfx
	mx2_xb_e2 = pf2am_e2 % halfx + halfx
	mx2_yb_e2 = pf2am_e2 / halfx
		

	# DEBUG
	print 'cell %d, max session 1 E1: %d / %d; E2 : %d / %d' % (NC, mx1_xb_e1, mx1_yb_e1, mx1_xb_e2, mx1_yb_e2)

	NC += 1
	pf1path = '%s%d_%s.mat' %(pfbase, NC, s1)
	pf2path = '%s%d_%s.mat' %(pfbase, NC, s2)

	# WORKAROUND
	#pf1path = '%spf_%d_%s.mat' %(pfbase, NC, s1)
	#pf2path = '%s../../14post%s/pfs_POST_1MIN/pf_%d_%s.mat' %(pfbase, full, NC, s2)

	# goals	
	#wd = os.getcwd()
	#os.chdir('..')
	[g1x, g1y, g2x, g2y, swap] = [float(f) for f in resolve_vars(['%{g1x}', '%{g1y}', '%{g2x}', '%{g2y}', '%{swap}'], True)]
	[sb1x, sb1y, sb2x, sb2y] = [float(f) for f in resolve_vars(['%{sb1x}', '%{sb1y}', '%{sb2x}', '%{sb2y}'], True)]

	d_sbg1 = np.sqrt((sb1x-g1x)**2 + (sb1y-g1y)**2)
	d_sbg2 = np.sqrt((sb2x-g2x)**2 + (sb2y-g2y)**2)
	
	swap = int(swap)
	#os.chdir(wd)

	if USECOM:
		print NC
		l1 = fcom1.readline().split(' ')[:4]
		l2 = fcom2.readline().split(' ')[:4]
		if len(l1) > 3 and len(l2) > 3:
			# print l1, l2
			[mx1_x_e1, mx1_y_e1, mx1_x_e2, mx1_y_e2] = [BS * float(f) for f in l1]
			[mx2_x_e1, mx2_y_e1, mx2_x_e2, mx2_y_e2] = [BS * float(f) for f in l2]
	else:
	# distances from goal to peak
		[mx1_x_e1, mx1_y_e1, mx2_x_e1, mx2_y_e1] = [BS * (c + 0.5) for c in [mx1_xb_e1, mx1_yb_e1, mx2_xb_e1, mx2_yb_e1]]
		[mx1_x_e2, mx1_y_e2, mx2_x_e2, mx2_y_e2] = [BS * (c + 0.5) for c in [mx1_xb_e2, mx1_yb_e2, mx2_xb_e2, mx2_yb_e2]]

	# print [mx1_x_e1, mx1_y_e1], [g1x, g1y]

	d_sbp[1-swap].append(distance([mx1_x_e1, mx1_y_e1], [sb1x, sb1y]))
	d_sbp[swap].append(distance([mx1_x_e2, mx1_y_e2], [sb2x, sb2y]))

	dist_s1[1-swap].append(distance([mx1_x_e1, mx1_y_e1], [g1x, g1y]) )
	dist_s2[1-swap].append(distance([mx2_x_e1, mx2_y_e1], [g1x, g1y]) )
	dist_s1[swap].append(distance([mx1_x_e2, mx1_y_e2], [g2x, g2y]) )
	dist_s2[swap].append(distance([mx2_x_e2, mx2_y_e2], [g2x, g2y]) )

	peakfrs_s1[1-swap].append(pf1[mx1_yb_e1, mx1_xb_e1])
	peakfrs_s2[1-swap].append(pf1[mx2_yb_e1, mx2_xb_e1])
	peakfrs_s1[swap].append(pf1[mx1_yb_e2, mx1_xb_e2])
	peakfrs_s2[swap].append(pf1[mx2_yb_e2, mx2_xb_e2])

	pkcr[1-swap].append([mx1_xb_e1, mx1_yb_e1, mx2_xb_e1, mx2_yb_e1])
	pkcr[swap].append([mx1_xb_e2, mx1_yb_e2, mx2_xb_e2, mx2_yb_e2])

	d_sbg[1-swap].append(d_sbg1)
	d_sbg[swap].append(d_sbg2)

print 'Mean dists session 1 con targ:', np.mean(dist_s1[0]), np.mean(dist_s1[1])
print 'Mean dists session 2 con targ:', np.mean(dist_s2[0]), np.mean(dist_s2[1])

# write distances to control / target before / after + peak firing rates in every environment

f = open(outpath, 'w')
for c in range(len(dist_s1[0])):
	# peakfr1_con   peakfr1_targ   peakfr2_con   peakfr2_targ   dist1_con   dist1_targ   dist2_con   dist2_targ
	#f.write((8 * '%f ' + '\n') % (peakfrs_s1[0][c], peakfrs_s1[1][c], peakfrs_s2[0][c], peakfrs_s2[1][c], dist_s1[0][c], dist_s1[1][c], dist_s2[0][c], dist_s2[1][c]))

	# 30.05 - add coordinates of peak
	f.write((20 * '%f ' + '\n') % (peakfrs_s1[0][c], peakfrs_s1[1][c], peakfrs_s2[0][c], peakfrs_s2[1][c], dist_s1[0][c], dist_s1[1][c], dist_s2[0][c], dist_s2[1][c], pkcr[0][c][0], pkcr[0][c][1], pkcr[0][c][2], pkcr[0][c][3], pkcr[1][c][0], pkcr[1][c][1], pkcr[1][c][2], pkcr[1][c][3], d_sbg[0][c], d_sbg[1][c], d_sbp[0][c], d_sbp[1][c]))
