#!/usr/bin/env python2

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
from numpy import genfromtxt
import os.path
from numpy import log
from call_log import log_call, log_and_print
from tracking_processing import distance
from iutils import *

# build mask for bins within the SB range
def sb_mask(sb1, sb2, radius):
	print sb1, sb2
        # FOR LFPO FIELDS
	#nbinsx = 66
	#nbinsy = 40
        nbinsx = 59
        nbinsy = 30
	binsize = 6
	sbm = np.zeros((nbinsy, nbinsx))
	for y in range(nbinsy):
		for x in range(nbinsx):
			binc = [x*binsize + binsize/2, y*binsize + binsize/2]
                        print binc
			if distance(binc, sb1) < radius or distance(binc, sb2) < radius:
				sbm[y, x] = 1
        plt.imshow(sbm)
        plt.show()
	return sbm.astype(bool)
			
def pfcorr_and_peakfrs(pf1, pf2, pfc):
	# take only non-inf and non-nan in both
	if PART:
		mask = np.invert( np.isnan(pf1) | np.isnan(pf2) | np.isinf(pf1) | np.isinf(pf2) | np.isinf(pfc) | np.isnan(pfc))
	else:
		mask = np.invert( np.isnan(pf1) | np.isnan(pf2) | np.isinf(pf1) | np.isinf(pf2) )

	# print pf1[mask]
	# print pf2[mask]

	if sum(mask) == 0:
		return np.nan, np.nan, np.nan, mask

	#if PART:
	#pfcorr = partial_correlation(pf1[mask], pf2[mask], pfc[mask])
	#else:
	pfcorr = np.corrcoef(pf1[mask], pf2[mask])[0,1]
	
	peakfr1 = max(pf1[mask]) * possr
	peakfr2 = max(pf2[mask]) * possr

	return pfcorr, peakfr1, peakfr2, mask
#==============================================================================================================================================================================================================

if len(argv) < 6 or len(argv) > 12:
	print 'Usage: (1)<path to directory containing directory pfs with place fields (2)<session 1> (3)<session 2> (4)<out path suffix> (5)<PFS root suf ([dir]/pf_)>'
	print 'OPTIONAL: -r <responses (optional)>; -p <control session for partial correlations>'
	print 'Requires: place fields in matrix format named pfs/pf_<cell_id>_<session>'
	print 'Requires(optionally): file named "responses" in the directory with light responses'
	exit(0)

argv = resolve_vars(argv)
op = parse_optional_params(argv[6:])

# find about, load start box coordinates and load / build SB mask
# maskpath = 'SB_BS6_1.mask' # THIS IS FOR LFPO PLACE FIELDS
print 'WARINING: using mask for python-generated place fields'
maskpath = 'SB_BS6_1.mask' # THIS IS FOR LFPO PLACE FIELDS
if not os.path.isfile(maskpath):
	abpath = 'about.txt'
	if not os.path.isfile(abpath):
		abpath = '../about.txt'
	if not os.path.isfile(abpath):
		print 'ERROR: about.txt not found'
		exit(1)

	sb1 = [0, 0]
	sb2 = [0, 0]
	estart = 0
	for line in open(abpath):
		ws = line.split(' ')
		if len(ws) < 2:
			continue
		if ws[0] == 'sb1x':
			sb1[0] = float(ws[1])
		if ws[0] == 'sb1y':
			sb1[1] = float(ws[1])
		if ws[0] == 'sb2x':
			sb2[0] = float(ws[1])
		if ws[0] == 'sb2y':
			sb2[1] = float(ws[1])
		if ws[0] == 'estart':
			estart = int(ws[1])

	print 'WARNING: SB coordinates will be scaled!'
	# starting env = ENV1
	#if estart == 0:
	#	scale2 = 1.039132
	#	scale1 = 1.16
	# starting env = ENV2
	#else:
	#	scale1 = 1.039132
	#	scale2 = 1.16

	# SCALE SB COORDS - dont' have to anymore, about.txt has scaled SB and goal coordinates
	#sb1[0] = sb1[0] * scale1
	#sb1[1] = sb1[1] * scale1
	#sb2[0] = (sb2[0] - 200) * scale2 + 200
	#sb2[1] = sb2[1] * scale2
	
        print 'DEBUG: sb coords = ', sb1, sb2
	sbmask = sb_mask(sb1, sb2, 30)
	np.savetxt(maskpath, sbmask)
else:
	sbmask = np.loadtxt(maskpath).astype(bool)
print sbmask

logdir = log_call(argv)

session1 = argv[2]
session2 = argv[3]

print 'WARNING: defulat values of 0 100 1 0 used for rate filter ... - parametrized not implemented'

# minimal peak firing rate filter - for all measures but 1st
MINPFR = 0 #float(argv[4])
# maximal peak firing rate filter - for all measures but 1st
MAXPFR = 100 #float(argv[5])
# maixmum peaf firing rate in the other environment - relative to the peak firing rate in the own environment - to filter for selectivity
MAXOPFR = 1 #float(argv[6])
# minimal firing rate in the second session - to filter out cells that increased the firing by much
MIN1PFR = 0 #float(argv[7])

OUTSUF = argv[4]

# root = argv[1] + 'pfs/pf_'
#rootsuf = 'pfs_BS6_FTS_2/pf_'
#print 'WARNING: hard-coded root path:', rootsuf
rootsuf = argv[5]

root = argv[1] + rootsuf 
# find out number of cells
c = 1
while os.path.isfile(root+str(c)+'_0.mat'):
	c += 1
NCELLS = c-1
# 1217 - 121, 1218 - 64, 1220 - 100, 1222 - 65
cells = range(1, NCELLS+1)
print 'NUMBER OF CELLS =', NCELLS

#responses = []
#if os.path.isfile(argv[1] + 'responses'):
#	responses = [float(r) for r in open(argv[1] + 'responses') if len(r) > 0]
#	print 'Loaded cell responses: ', responses
#elif len(argv) > 9:

responses = [float(r) for r in open(gdv(op, 'r'))]
# responses = responses[1:]
print 'Loaded %d responses' % len(responses)

batch2 = gdv(op, 'batch2')
if batch2 != '':
	root2 = argv[1] + 'pfs_' + batch2 + '/pf_'
else:
	root2 = root
print 'root2=', root2


if root2 != root:
        c = 1
        while os.path.isfile(root2+str(c)+'_0.mat'):
                c += 1
        if c-1 < NCELLS:
                NCELLS = c-1
                cells = range(1, NCELLS+1)

pfss = []
peakfrs = []
pfss1 = []
pfss2 = []
peakfrs1 = []
peakfrs2 = []
peakfrsall1 = []
peakfrsall2 = []
peakfrs_e1_s0 = []
peakfrs_e1_s1 = []
peakfrs_e2_s0 = []
peakfrs_e2_s1 = []
meanrates = []
# calculated for each environment separately for each cell
pfss_e1 = []
pfss_e2 = []
# to multiply firing rate in the dumped place fields == position sampling firing rate
possr = 50 # 50 for LFPO place fields, 1 for python place fields
print 'WARNING: RATES IN MAPS MULTIPLIED BY POSITION SAMPLING RATE = ', possr

# currently computed:
#	peak firing rates in both sessions over both environments
# 	PFS accross sessions of the common map

ignored = 0

print 'Number of cells: %d' %  len(cells)

PART = ('p' in op)
if PART:
	session_c = op['p']

for c in cells:

	# place fields for 1st and 2nd session
	pf1m = genfromtxt(root + str(c) + '_' + session1 + '.mat')
	pf2m = genfromtxt(root2 + str(c) + '_' + session2 + '.mat')
	if PART:
		# cpmtrp;
		pfcm = genfromtxt(root2 + str(c) + '_' + session_c + '.mat')

	# as a template for occupancy ! : pf / end learning 
	pf_el_occ = genfromtxt(root2 + 'occ_5.mat')

        # cut mask if it is larger - with WARNING
        if sbmask.shape != pf1m.shape:
            print 'WARNING: mask dimesinos dont match PF dimensions - cut mask'
            sbmask = sbmask[:pf1m.shape[0], :pf1m.shape[1]]

	# MASK
	print 'WARNING: START BOX AREA EXCLUDED'
	pf1m[sbmask] = np.nan
	pf2m[sbmask] = np.nan

	print 'WARNING: bins, uncoccupied in the end of nwe learning, excluded ...'
	pf1m[pf_el_occ < 1] = np.nan
	pf2m[pf_el_occ < 1] = np.nan
	
	if len(pf1m.shape) < 2:	
		pf1m = np.reshape(pf1m, (1, -1))
		pf2m = np.reshape(pf2m, (1, -1))
		# print 'Reshaped to: ', pf1m.shape
	shape = pf1m.shape
	#print shape
	w = shape[1]

	sm1 = np.nansum(pf_el_occ[:,:w/2])
	sm2 = np.nansum(pf_el_occ[:,w/2:])
	print sm1, sm2

	# mean firing rates

	pf1m_occ = pf1m * pf_el_occ
	pf1m_occ[np.isinf(pf1m_occ)] = np.nan
	mr1_e1 = np.nansum(pf1m_occ[:,:w/2]) / sm1
	mr1_e2 = np.nansum(pf1m_occ[:,w/2:]) / sm2
	pf2m_occ = pf2m * pf_el_occ
	pf2m_occ[np.isinf(pf2m_occ)] = np.nan
	mr2_e1 = np.nansum(pf2m_occ[:,:w/2]) / sm1 
	mr2_e2 = np.nansum(pf2m_occ[:,w/2:]) / sm2
	meanrates.append([possr * mr1_e1, possr * mr1_e2, possr * mr2_e1, possr * mr2_e2])

	# linearize
	pf1 = pf1m.flatten()
	pf2 = pf2m.flatten()

	if PART:
		pfcm[sbmask] = np.nan
		pfcm[pf_el_occ < 1] = np.nan
		if len(pfcm.shape) < 2:
			pfcm = np.reshape(pfc, (1, -1))
		pfc = pfcm.flatten()

	# place field similarit and peak firing rate (MAX OF 2 ENV) in every session
	pfcorr, peakfr1, peakfr2, mask = pfcorr_and_peakfrs(pf1, pf2, pfc if PART else 0)
	# PFS and PEAK FRs by environment
	pfs_e1, peakfr_e1_s0, peakfr_e1_s1, tmp3 = pfcorr_and_peakfrs(pf1m[:,0:w/2].flatten(), pf2m[:,0:w/2].flatten(), pfcm[:,0:w/2].flatten() if PART else 0)
	pfs_e2, peakfr_e2_s0, peakfr_e2_s1, tmp3 = pfcorr_and_peakfrs(pf1m[:,w/2:].flatten(), pf2m[:,w/2:].flatten(), pfcm[:, w/2:].flatten() if PART else 0)

	# need to keep all for consistency
	#if np.isnan(pfcorr):
	#	log_and_print(logdir, 'NAN overall simlairty for cell %d, ignore' % c)
	#	log_and_print(logdir, 'cell: %d, ignored: %d ' % (c, ignored))
	#	if len(responses) > 0:
	#		del responses[c-1-ignored]
	#	ignored += 1
	#
	#	continue

	# store peak FR per env per session
	peakfrs_e1_s0.append(peakfr_e1_s0)
	peakfrs_e1_s1.append(peakfr_e1_s1)
	peakfrs_e2_s0.append(peakfr_e2_s0)
	peakfrs_e2_s1.append(peakfr_e2_s1)

	peakfrsall1.append(peakfr1)
	peakfrsall2.append(peakfr2)	

	log_and_print(logdir, 'Place field similarity for cell %d = %.2f; peak FR (Hz) = %.2f / %.2f; pfs by environment: %.2f / %.2f' % (c, pfcorr, peakfr1, peakfr2, pfs_e1, pfs_e2))

	pfss.append(pfcorr)
	peakfrs.append(max(peakfr1, peakfr2))

	# find out which environment and add to corresponding arrays if peak in the same environment in both sessions
	pf1[np.invert(mask)] = 0
	pf2[np.invert(mask)] = 0
	pf1m = pf1.reshape(shape)
	pf2m = pf2.reshape(shape)

	# TODO : group cells by average firing rate [bin-wise] ... - can be unfair for different coverage ...
	# sum1_s1 = np.sum(pf1m[:,0:w/2]) / NUMBER ... [AVG]
	# sum2_s1 = np.sum(pf1m[:,w/2:])
	# sum1_s2 = np.sum(pf2m[:,0:w/2])
	# sum2_s2 = np.sum(pf2m[:,w/2:])
	
	# whichever has largest TOTAL / MAX firing
	pfss_e1.append(pfs_e1)
	pfss_e2.append(pfs_e2)


pfss = np.array(pfss)
peakfrs = np.array(peakfrs)
# TODO substitute with indices: pfr_e1 > pfr_e2 & ...
peakfrsall1 = np.array(peakfrsall1)
peakfrsall2 = np.array(peakfrsall2)
pfss_e1 = np.array(pfss_e1)
pfss_e2 = np.array(pfss_e2)
peakfrs_e1_s0 = np.array(peakfrs_e1_s0)
peakfrs_e1_s1 = np.array(peakfrs_e1_s1)
peakfrs_e2_s0 = np.array(peakfrs_e2_s0)
peakfrs_e2_s1 = np.array(peakfrs_e2_s1)

log_and_print(logdir, 'PFS mean by environment (all cells): %.3f / %.3f\n' % (np.nanmean(pfss_e1), np.nanmean(pfss_e2)))
# !!! TODO: above + filetred by rate !!!
# ! BELOW: STD WITH SAME CELLS - FIX INDEXING !
log_and_print(logdir, 'PFS mean and std of cells with PFR in range [ %.2f; %.2f] : %f +- %f' % (MINPFR, MAXPFR, np.nanmean(pfss[(peakfrs > MINPFR) & (peakfrs < MAXPFR)]), np.nanstd(pfss)))
log_and_print(logdir, 'Correlation of PFS and peak FR: %.2f\n' % np.corrcoef(pfss, peakfrs)[1,0])

log_and_print(logdir, 'PFS mean by environment ([MINPFR; MAXPFR]): %.3f / %.3f' % (np.nanmean(pfss_e1[(peakfrs_e1_s0 > MINPFR) & (peakfrs_e1_s0 < MAXPFR) & (peakfrs_e1_s1 > MINPFR) & (peakfrs_e1_s1 < MAXPFR)]), np.nanmean(pfss_e2[(peakfrs_e1_s0 > MINPFR) & (peakfrs_e1_s1 > MINPFR) & (peakfrs_e1_s0 < MAXPFR) & (peakfrs_e1_s1 < MAXPFR)])))
log_and_print(logdir, 'PFS for COMBINED MAP( BOTH ENVIRONMENTS) FR_e1 > FR_e2 vs. FR_e2 > FR_e1, PFR in [MIN; MAX]: %f / %f\n' % (np.nanmean(pfss[(peakfrs_e1_s0 > peakfrs_e2_s0) & (peakfrs > MINPFR) & (peakfrs < MAXPFR)]), np.nanmean(pfss[(peakfrs_e2_s0 > peakfrs_e1_s0) &(peakfrs > MINPFR) & (peakfrs < MAXPFR)])))

# absolute MAXOPFR
#cells_e1_high_e2_low_s0 = (peakfrs_e1_s0 > MINPFR) & (peakfrs_e1_s0 < MAXPFR) & (peakfrs_e2_s0 < MAXOPFR) & (peakfrs_e1_s1 > MIN1PFR)
#cells_e2_high_e1_low_s0 = (peakfrs_e2_s0 > MINPFR) & (peakfrs_e2_s0 < MAXPFR) & (peakfrs_e1_s0 < MAXOPFR) & (peakfrs_e2_s1 > MIN1PFR)
# relative MAXOPFR
cells_e1_high_e2_low_s0 = (peakfrs_e1_s0 > MINPFR) & (peakfrs_e1_s0 < MAXPFR) & (peakfrs_e2_s0 < peakfrs_e1_s0 / MAXOPFR) & (peakfrs_e1_s1 > MIN1PFR)
cells_e2_high_e1_low_s0 = (peakfrs_e2_s0 > MINPFR) & (peakfrs_e2_s0 < MAXPFR) & (peakfrs_e1_s0 < peakfrs_e2_s0 / MAXOPFR) & (peakfrs_e2_s1 > MIN1PFR)

log_and_print(logdir, 'RESULTS FOR CELLS WITH HIGH PFR IN ONE ENV AND LOW IN ANOTHER (IN S0) [%d/%d cells for E1/E2]:\n' % (sum(cells_e1_high_e2_low_s0), sum(cells_e2_high_e1_low_s0)))
log_and_print(logdir, '.. IN COMBINED MAP: %.2f / %.2f' % (np.nanmean(pfss[cells_e1_high_e2_low_s0]), np.nanmean(pfss[cells_e2_high_e1_low_s0])))
log_and_print(logdir, '.. IN OWN MAP: %.2f / %.2f' % (np.nanmean(pfss_e1[cells_e1_high_e2_low_s0]), np.nanmean(pfss_e2[cells_e2_high_e1_low_s0])))
log_and_print(logdir, '.. IN OTHER MAP: %.2f / %.2f\n' % (np.nanmean(pfss_e1[cells_e2_high_e1_low_s0]), np.nanmean(pfss_e2[cells_e1_high_e2_low_s0])))

#if len(responses) > 0:
#	log_and_print(logdir, 'Len of responses: %d / len of pfss: %d' % (len(responses), len(pfss)))
#	responses = np.array(responses)
#	# try those with high / low firing rates etc.
#	log_and_print(logdir, 'Correlation of PFS and responses: %.3f' % np.corrcoef(responses[:], pfss[:])[0, 1])
#	log_and_print(logdir, 'Correlation of inhibited cells PFS and responses (%d cells): %.2f' % (sum(responses > 1), np.corrcoef(responses[responses > 1], pfss[responses > 1])[0, 1]))
#	log_and_print(logdir, 'Correlation of disinhibited cells PFS and responses (%d cells): %.2f' % (sum(responses < 1), np.corrcoef(responses[responses < 1], pfss[responses < 1])[0, 1]))

# PFS env-wise from Las
#plt.scatter(responses, pfss_e1, s=50) # c = peakfrs
#plt.scatter(responses, pfss_e2, c='red', s=50)
inds = ((pfss_e1 > 0) | (pfss_e2 > 0)) & (peakfrs > 0.5)
log_and_print(logdir, 'Using %d out of %d cells' % (sum(inds), len(pfss)))
#f, (ax1, ax2) = plt.subplots(1, 2, sharey = True)
#ax1.scatter(responses[inds], pfss_e1[inds], c=peakfrs[inds], s=40)
#ax2.scatter(responses[inds], pfss_e2[inds], c=peakfrs[inds], s=40)

print 'DUMP'
outpath = 'PFS_%s_%s%s.out' % (session1, session2, OUTSUF)
if os.path.isfile(outpath):
	print 'ERROR: File', outpath, 'exists, delete before runnign the script or choose a different output path'
	exit(1)
fo = open(outpath, 'w')
for i in range(pfss.shape[0]):
	#fo.write('%f %f %f %f %f %f %f %f\n' % (pfss[i], pfss_e1[i], pfss_e2[i], peakfrs_e1_s0[i], peakfrs_e2_s0[i], peakfrs_e1_s1[i], peakfrs_e2_s1[i], responses[i]))
	fo.write('%f %f %f %f %f %f %f %f %f %f %f %f\n' % (pfss[i], pfss_e1[i], pfss_e2[i], peakfrs_e1_s0[i], peakfrs_e2_s0[i], peakfrs_e1_s1[i], peakfrs_e2_s1[i], responses[i], meanrates[i][0], meanrates[i][1], meanrates[i][2], meanrates[i][3]))
fo.close()

if len(responses) == 0:
	print 'WARNING: no light responses provided, finish here'
	exit(0)

print 'Sizes of responses / pfss_e1: %d / %d' % (len(responses), pfss_e1.shape[0])
if len(responses) > pfss_e1.shape[0]:
	responses = responses[:pfss_e1.shape[0]]
	print 'WARNING: TRIP RESPONSES'

responses = np.array(responses)
plt.scatter(responses[inds], pfss_e1[inds]-pfss_e2[inds], c=log(peakfrs[inds]), s=60)
ravg_pfss_e1 = np.convolve(pfss_e1[np.argsort(responses)], np.ones(5,), mode='valid') / 5
ravg_pfss_e2 = np.convolve(pfss_e2[np.argsort(responses)], np.ones(5,), mode='valid') / 5
#for i in range(0, len(responses)):
#	plt.plot([responses[i], responses[i]], [pfss_e1[i], pfss_e2[i]], c='black')
#plt.plot(np.sort(responses)[2:-2], ravg_pfss_e1, c='b')
#plt.plot(np.sort(responses)[2:-2], ravg_pfss_e2, c='r')
plt.xlabel('Laser response')
plt.ylabel('PFS')
plt.suptitle('PFS vs. Laser response, color = Peak FR')
# plt.show()

#plt.scatter(pfss_e1, pfss_e2, c=np.log(peakfrsall1/peakfrsall2), s=50)
#plt.xlabel('PFS env 1')
#plt.ylabel('PFS env 2')
#plt.suptitle('Color = Peak Firing rate ratio')

#plt.scatter(peakfrsall1, peakfrsall2, c=pfss, s=50)
#plt.xlabel('Peak firing rate 1')
#plt.ylabel('Peak firing rate 2')
#plt.suptitle('PFS')

#plt.scatter(peakfrs1, pfss1)

#plt.scatter(peakfrs2, pfss2, color='r')

#plt.scatter(peakfrs, pfss)
#plt.xlabel('Peak Firing Rate')
#plt.ylabel('PFS')
#plt.suptitle('PFS vs. Peak FR')


#plt.hist(pfss, 20)
#plt.show()
