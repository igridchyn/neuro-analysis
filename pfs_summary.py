#!/usr/bin/env python2

import warnings
from sys import argv
from math import sqrt
from matplotlib import pyplot as plt
import numpy as np
from numpy import genfromtxt
import os.path
from numpy import log
from call_log import * 
from scipy.stats import ttest_rel, ttest_ind, wilcoxon, ks_2samp, mannwhitneyu

def psig(p):
	if p < 0.001:
                return ' **** '
        elif p < 0.005:
                return ' ***  '
        elif p < 0.01:
                return ' **   '
        elif p < 0.05:
                return ' *    '
        elif p < 0.1:
                return ' ^    '
        else:
		return '      '

def append_to_array(a, v1, v2):
	#stack = np.vstack((v1, v2))
	#return np.concatenate((a, stack), axis = 1)
	a[0].extend(v1)
	a[1].extend(v2)

	# workaround - write to the day output file

	foutday.write('%d\n' % len(v1))
	for v in v1:
		foutday.write('%.3f\n' % v)	
	foutday.write('%d\n' % len(v2))
	for v in v2:
		foutday.write('%.3f\n' % v)

        # foutday.write('%.3f %.3f\n' % (np.mean(v1), np.mean(v2)))

	return a

warnings.filterwarnings("ignore",category = RuntimeWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
if len(argv) < 8:
	print 'USAGE: (1)<MIN PFR> (2)<MAX PFR> (3)<OTHER PFR X TIME SMALLER MAX> (4)<MIN SESSION 1 PFR> (5)<MINREPS> (6)<PFS FILT> (7)<MAX PFS> (8)<PFS FILES> (9)<OUTPUT SUF>'
	print 'OUTPUT: file with values for measure 7 + append means to file PFS_SUMMARY.out, output day-wise means to PFS_MEAN.txt in every day directory'
	exit(0)
	
ld = log_call(argv)

MINPFR = float(argv[1])
MAXPFR = float(argv[2])
MAXOPFR = float(argv[3])
MIN1PFR = float(argv[4])
if ';' not in argv[5]:
	MINRESP = float(argv[5])
else:
	MINRESP = 0
PFSFILTPATH = argv[6]

pfs_by_env = [[], []]
pfs_pfr_filt = [[], []]
pfs_comb_dom = [[], []]

pfs_sel_comb = [[], []]
pfs_sel_own = [[], []]
pfs_sel_other = [[], []]

# place field similarities of place cells in every environment
pfs_pcs = [[], []]
# same but fr filtered
pfs_pcs_filt = [[], []]

swap = []

msgmissing = ''

REMAPMAX = float(argv[7])
print 'WARNING: using fixed sparsity  limit < 0.3'
print 'WARNING: using fixed remapping limit < %.2f' % REMAPMAX

celltot = 0

# count how many cells pass filtering criteria
pass_resp = 0
pass_coh = 0
pass_spars = 0
pass_sel = 0
pass_pfrs_both = 0
pass_pfrs_first = 0
# env-wise passing of coherence / sparsity
pass_e1ch = 0
pass_e2ch = 0
pass_pfs_e1 = 0
pass_pfs_e2 = 0

#if len(argv) < 10:
dirlist = [os.path.expandvars(line[:-1]) for line in open(argv[8])]
# load from file and replace environmental variables
#else:
#	dirlist = argv[8:]

sresp = argv[5]
if sresp == '0':
	RAPP = 'A'
elif ';' in sresp:
	RAPP = 'U'
elif '-' in sresp:
	RAPP = 'I'
else:
	RAPP = 'D'	

OUTSUF = ''
if len(argv) > 9:
	OUTSUF = argv[9]

dcnt = -1
indall_t = []
indall_c = []
for path in dirlist:
	dcnt += 1

	if len(path) < 2:
		print 'WARNING: SKIP PATH = ', path
		continue

	LOAD_IDX = False
	#if len(argv) > 9:
	#	print 'LOAD IDX!'
	#	IDX_C = np.loadtxt(os.path.dirname(path) + '/C_8_%s.ind' % RAPP)
	#	IDX_T = np.loadtxt(os.path.dirname(path) + '/T_8_%s.ind' % RAPP)
	#	IDX_C = IDX_C.astype(bool)
	#	IDX_T = IDX_T.astype(bool)
	#	LOAD_IDX = True

	pfss = []
	pfss_e1 = []
	pfss_e2 = []
	meanfrs_e1_s0 = []
	meanfrs_e2_s0 = []
	meanfrs_e1_s1 = []
	meanfrs_e2_s1 = []
	meanfrs = []
	responses = []
	sparsity1 = []
	coherence1 = []
	sparsity2 = []
	coherence2 = []
	sparsity1s2 = []
	coherence1s2 = []
	sparsity2s2 = []
	coherence2s2 = []
	pfsfilt_e1 = []
	pfsfilt_e2 = []
	lmeanfrs = []

	if not os.path.isfile(path):
		print 'WARNING: file ', path, ' not found, skip to next one...'
		msgmissing += path + ', '
		continue
	
	fspars1 = open(os.path.dirname(path) + '/sparsity_BS6_OT5_E1.txt')
	fcoh1 = open(os.path.dirname(path) + '/coherence_BS6_OT5_E1.txt')
	fspars2 = open(os.path.dirname(path) + '/sparsity_BS6_OT5_E2.txt')
	fcoh2 = open(os.path.dirname(path) + '/coherence_BS6_OT5_E2.txt')
	fspars1s2 = open(os.path.dirname(path) + '/sparsity_BS6_OT5_E1_NL1.txt')
	fcoh1s2 = open(os.path.dirname(path) + '/coherence_BS6_OT5_E1_NL1.txt')
	fspars2s2 = open(os.path.dirname(path) + '/sparsity_BS6_OT5_E2_NL1.txt')
	fcoh2s2 = open(os.path.dirname(path) + '/coherence_BS6_OT5_E2_NL1.txt')
	fpfsfilt = open(os.path.dirname(path) + '/' + PFSFILTPATH)
        print 'pfsfilt path = ', os.path.dirname(path) + '/' + PFSFILTPATH

	log_file(ld, path, False)

	for line in open(path):
		vals = [float(w) for w in line.split(' ')]
		pfss.append(vals[0])
		pfss_e1.append(vals[1])
		pfss_e2.append(vals[2])
		meanfrs_e1_s0.append(vals[3])
		meanfrs_e2_s0.append(vals[4])
		meanfrs_e1_s1.append(vals[5])
		meanfrs_e2_s1.append(vals[6])
		meanfrs.append(max(vals[3:7]))
		responses.append(vals[7])
		
		if len(vals) > 8:
			lmeanfrs.append(vals[8:12])
		else:
			print 'ERROR: no meanfrs ...'
			exit(1)

		sparsity1.append(float(fspars1.readline()))
		coherence1.append(float(fcoh1.readline()))
		sparsity2.append(float(fspars2.readline()))
		coherence2.append(float(fcoh2.readline()))
		sparsity1s2.append(float(fspars1s2.readline()))
		coherence1s2.append(float(fcoh1s2.readline()))
		sparsity2s2.append(float(fspars2s2.readline()))
		coherence2s2.append(float(fcoh2s2.readline()))

		wspfsfilt = fpfsfilt.readline().split(' ')
		pfsfilt_e1.append(float(wspfsfilt[1]))
		pfsfilt_e2.append(float(wspfsfilt[2]))

	meanfrs_e1_s0 = [l[0] for l in lmeanfrs]
	meanfrs_e2_s0 = [l[1] for l in lmeanfrs]
	meanfrs_e1_s1 = [l[2] for l in lmeanfrs]
	meanfrs_e2_s1 = [l[3] for l in lmeanfrs]

	meanfrs = np.array(meanfrs)
	pfss = np.array(pfss)
	pfss_e1 = np.array(pfss_e1)
	pfss_e2 = np.array(pfss_e2)
	meanfrs_e1_s0 = np.array(meanfrs_e1_s0)
	meanfrs_e1_s1 = np.array(meanfrs_e1_s1)
	meanfrs_e2_s0 = np.array(meanfrs_e2_s0)
	meanfrs_e2_s1 = np.array(meanfrs_e2_s1)
	responses = np.array(responses)
	sparsity1 = np.array(sparsity1)
	coherence1 = np.array(coherence1)
	sparsity2 = np.array(sparsity2)
	coherence2 = np.array(coherence2)
	sparsity1s2 = np.array(sparsity1s2)
	coherence1s2 = np.array(coherence1s2)
	sparsity2s2 = np.array(sparsity2s2)
	coherence2s2 = np.array(coherence2s2)

	sparsind1 = ~np.isnan(sparsity1) & ~np.isnan(sparsity1s2) & ((sparsity1 < 0.3) | (sparsity1s2 < 0.3)) # 0.3
	cohind1 = ~np.isnan(coherence1) & ~np.isnan(coherence1s2) & ((coherence1 > 0.5) | (coherence1s2 > 0.5)) # 0.5
	sparsind2 = ~np.isnan(sparsity2) & ~np.isnan(sparsity2s2) & ((sparsity2 < 0.3) | (sparsity2s2 < 0.3)) # 0.3
	cohind2 = ~np.isnan(coherence2) & ~np.isnan(coherence2s2) & ((coherence2 > 0.5) | (coherence2s2 > 0.5)) # 0.5

	# print meanfrs
	celltot += len(pfss)

	sresp = argv[5]	
	if sresp == '0':
		respind = [True] * len(responses)
	elif ';' in sresp:
		cp = sresp.find(';')
		minr = float(sresp[:cp])
		maxr = float(sresp[cp+1:])
		#print 'Min, max responses: %.2f / %.2f' % (minr, maxr)
		respind = (responses > minr) & (responses < maxr)
	elif argv[5].startswith('+'):
		respind = np.abs(responses) < MINRESP
		print 'WARNING: USING ABSOLUTE RESPONSE FILTER <<<<'
	elif MINRESP > 0:
		respind = responses > MINRESP
	elif argv[5] == '0':
		respind = ~np.isnan(responses)
	else:
		respind = responses < MINRESP

	pass_resp += np.sum(respind)

	apath = os.path.dirname(path) + '/about.txt'
	for line in open(apath):
		if line.startswith('swap'):
			swap.append(bool(int(line.split(' ')[-1])))
			# DEBUG
			# print 'Swap ', swap[-1]
			swp = swap[-1]

	if REMAPMAX < 1.0:
		pfsind1 = np.array(pfsfilt_e1) < REMAPMAX
		pfsind2 = np.array(pfsfilt_e2) < REMAPMAX
	else:
		pfsind1 = np.array([True] * len(pfsfilt_e1))
		pfsind2 = np.array([True] * len(pfsfilt_e2))

	pass_pfs_e1 += np.sum(pfsind1)
	pass_pfs_e2 += np.sum(pfsind2)

	# only measure 3
	filtind = respind & (sparsind1 | sparsind2) & (cohind1 | cohind2)
	# all other measures
	filtind1 = respind & sparsind1 & cohind1 & pfsind1
	filtind2 = respind & sparsind2 & cohind2 & pfsind2

	pass_e1ch += np.sum(cohind1 & sparsind1)
	pass_e2ch += np.sum(cohind2 & sparsind2)
	pass_coh += np.sum(cohind1 | cohind2)
	pass_spars += np.sum(sparsind1 | sparsind2)

	# write filetered values (or means) to file
	foutday = open(os.path.dirname(path) + '/PFS_MEAN.txt', 'w')

	pass_pfrs_first += np.sum((meanfrs_e1_s0 < MAXPFR) & (meanfrs_e1_s0 > MINPFR) | (meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s0 < MAXPFR))

	# measure 1
	if swp:
		pfs_by_env = append_to_array(pfs_by_env, pfss_e2[filtind2], pfss_e1[filtind1])
	else:
		pfs_by_env = append_to_array(pfs_by_env, pfss_e1[filtind1], pfss_e2[filtind2])

	# measure 2
	if swp:
		pfs_pfr_filt = append_to_array(pfs_pfr_filt, pfss_e2[(meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s0 < MAXPFR) & (meanfrs_e2_s1 > MINPFR) & (meanfrs_e2_s1 < MAXPFR) & filtind2], pfss_e1[(meanfrs_e1_s0 > MINPFR) & (meanfrs_e1_s1 > MINPFR) & (meanfrs_e1_s0 < MAXPFR) & (meanfrs_e1_s1 < MAXPFR) & filtind1])
	else:
		pfs_pfr_filt = append_to_array(pfs_pfr_filt, pfss_e1[(meanfrs_e1_s0 > MINPFR) & (meanfrs_e1_s0 < MAXPFR) & (meanfrs_e1_s1 > MINPFR) & (meanfrs_e1_s1 < MAXPFR) & filtind1], pfss_e2[(meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s1 > MINPFR) & (meanfrs_e2_s0 < MAXPFR) & (meanfrs_e2_s1 < MAXPFR) & filtind2])

	pass_pfrs_both += np.sum((meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s0 < MAXPFR) & (meanfrs_e2_s1 > MINPFR) & (meanfrs_e2_s1 < MAXPFR)  |  (meanfrs_e1_s0 > MINPFR) & (meanfrs_e1_s1 > MINPFR) & (meanfrs_e1_s0 < MAXPFR) & (meanfrs_e1_s1 < MAXPFR))

	# measure 3
	if swp:
		pfs_comb_dom = append_to_array(pfs_comb_dom, pfss[(meanfrs_e2_s0 > meanfrs_e1_s0) & (meanfrs > MINPFR) & (meanfrs < MAXPFR) & filtind], pfss[(meanfrs_e1_s0 > meanfrs_e2_s0) &(meanfrs > MINPFR) & (meanfrs < MAXPFR) & filtind])
	else:
		pfs_comb_dom = append_to_array(pfs_comb_dom, pfss[(meanfrs_e1_s0 > meanfrs_e2_s0) & (meanfrs > MINPFR) & (meanfrs < MAXPFR) & filtind], pfss[(meanfrs_e2_s0 > meanfrs_e1_s0) &(meanfrs > MINPFR) & (meanfrs < MAXPFR) & filtind])

	# absolute MAXOPFR
	#cells_e1_high_e2_low_s0 = (meanfrs_e1_s0 > MINPFR) & (meanfrs_e1_s0 < MAXPFR) & (meanfrs_e2_s0 < MAXOPFR) & (meanfrs_e1_s1 > MIN1PFR)
	#cells_e2_high_e1_low_s0 = (meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s0 < MAXPFR) & (meanfrs_e1_s0 < MAXOPFR) & (meanfrs_e2_s1 > MIN1PFR)
	# relative MAXOPFR
	cells_e1_high_e2_low_s0 = (meanfrs_e1_s0 > MINPFR) & (meanfrs_e1_s0 < MAXPFR) & (meanfrs_e2_s0 < meanfrs_e1_s0 / MAXOPFR) & (meanfrs_e1_s1 > MIN1PFR) & filtind1
	cells_e2_high_e1_low_s0 = (meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s0 < MAXPFR) & (meanfrs_e1_s0 < meanfrs_e2_s0 / MAXOPFR) & (meanfrs_e2_s1 > MIN1PFR) & filtind2

	pass_sel += np.sum((meanfrs_e1_s0 < meanfrs_e2_s0 / MAXOPFR) | (meanfrs_e2_s0 < meanfrs_e1_s0 / MAXOPFR))

	# measure 4
	if swp:
		pfs_sel_comb = append_to_array(pfs_sel_comb, pfss[cells_e2_high_e1_low_s0], pfss[cells_e1_high_e2_low_s0])
	else:
		pfs_sel_comb = append_to_array(pfs_sel_comb, pfss[cells_e1_high_e2_low_s0], pfss[cells_e2_high_e1_low_s0])		
	# measure 5
	if swp:
		pfs_sel_own = append_to_array(pfs_sel_own, pfss_e2[cells_e2_high_e1_low_s0], pfss_e1[cells_e1_high_e2_low_s0])
	else:
		pfs_sel_own = append_to_array(pfs_sel_own, pfss_e1[cells_e1_high_e2_low_s0], pfss_e2[cells_e2_high_e1_low_s0])
	# measure 6
	if swp:
		pfs_sel_other = append_to_array(pfs_sel_other, pfss_e2[cells_e1_high_e2_low_s0], pfss_e1[cells_e2_high_e1_low_s0])
	else:
		pfs_sel_other = append_to_array(pfs_sel_other, pfss_e1[cells_e2_high_e1_low_s0], pfss_e2[cells_e1_high_e2_low_s0])

	# measure 7
	if swp:
		pfs_pcs = append_to_array(pfs_pcs, pfss_e2[filtind2], pfss_e1[filtind1])
	else:
		pfs_pcs = append_to_array(pfs_pcs, pfss_e1[filtind1], pfss_e2[filtind2])

	# measure 8
	if LOAD_IDX:
		if swp:
			pfs_pcs_filt = append_to_array(pfs_pcs_filt, pfss_e2[IDX_T], pfss_e1[IDX_C])
		else:
			pfs_pcs_filt = append_to_array(pfs_pcs_filt, pfss_e1[IDX_T], pfss_e2[IDX_C])
	else:
		if swp:
			pfs_pcs_filt = append_to_array(pfs_pcs_filt, pfss_e2[filtind2 & (meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s0 < MAXPFR)], pfss_e1[filtind1 & (meanfrs_e1_s0 < MAXPFR) & (meanfrs_e1_s0 > MINPFR)])
		else:
			pfs_pcs_filt = append_to_array(pfs_pcs_filt, pfss_e1[filtind1 & (meanfrs_e1_s0 < MAXPFR) & (meanfrs_e1_s0 > MINPFR)], pfss_e2[filtind2 & (meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s0 < MAXPFR)])

	ind8_e1 = filtind1 & (meanfrs_e1_s0 < MAXPFR) & (meanfrs_e1_s0 > MINPFR)
	ind8_e2 = filtind2 & (meanfrs_e2_s0 > MINPFR) & (meanfrs_e2_s0 < MAXPFR)
	# save indices for use in other analyses

	# append to list of indices
	for i in range(len(ind8_e1)):
		if ind8_e1[i]:
			if swp:			
				indall_c.append(str(dcnt) + '000' + str(i))
			else:
				indall_t.append(str(dcnt) + '000' + str(i))
			
	for i in range(len(ind8_e2)):
		if ind8_e2[i]:
			if swp:			
				indall_t.append(str(dcnt) + '000' + str(i))
			else:
				indall_c.append(str(dcnt) + '000' + str(i))
			
	if not LOAD_IDX:
		if swp:
			np.savetxt(os.path.dirname(path) + '/C_8_%s.ind' % RAPP, ind8_e1)
			np.savetxt(os.path.dirname(path) + '/T_8_%s.ind' % RAPP, ind8_e2)
		else:
			np.savetxt(os.path.dirname(path) + '/T_8_%s.ind' % RAPP, ind8_e1)
			np.savetxt(os.path.dirname(path) + '/C_8_%s.ind' % RAPP, ind8_e2)

	# PFS env-wise from Las
	#plt.scatter(responses, pfss_e1, s=50) # c = meanfrs
	#plt.scatter(responses, pfss_e2, c='red', s=50)
	#print 'WARNING: LIMIT HARDCODE'
	#inds = ((pfss_e1 > 0.5) | (pfss_e2 > 0.5)) & (meanfrs > 3)
	#log_and_print(logdir, 'Using %d out of %d cells' % (sum(inds), len(pfss)))
	#f, (ax1, ax2) = plt.subplots(1, 2, sharey = True)
	#ax1.scatter(responses[inds], pfss_e1[inds], c=meanfrs[inds], s=40)
	#ax2.scatter(responses[inds], pfss_e2[inds], c=meanfrs[inds], s=40)

	#if len(responses) == 0:
	#	print 'WARNING: no light responses provided, finish here'
	#	exit(0)
	#plt.scatter(responses[inds], pfss_e1[inds]-pfss_e2[inds], c=log(meanfrs[inds]), s=60)
	#ravg_pfss_e1 = np.convolve(pfss_e1[np.argsort(responses)], np.ones(5,), mode='valid') / 5

ftot = float(celltot) / 100
print 'Percentage of cells passing criteria:'
print '   %.1f%% coherence' % (pass_coh / ftot)
print '   %.1f%% sparsity' % (pass_spars / ftot)
print '   %.1f%% response' % (pass_resp/ ftot)
print '   %.1f%% selectivity' % (pass_sel/ ftot)
print '   %.1f%% pfrs both sessions' % (pass_pfrs_both/ ftot)
print '   %.1f%% pfrs first session' % (pass_pfrs_first/ ftot)
print '   %.1f%% coherence & sparsity E1' % (pass_e1ch / ftot)
print '   %.1f%% coherence & sparsity E2' % (pass_e2ch / ftot)
print '   %.1f%% PFS E1' % (pass_pfs_e1 / ftot)
print '   %.1f%% PFS E2' % (pass_pfs_e2 / ftot)

print 'SWAP: ', swap

# swap - done above
#for i in range(len(swap)):
#	if swap[i]:
#		pfs_by_env[i] = list(reversed(pfs_by_env[i]))
#		pfs_pfr_filt[i] = list(reversed(pfs_pfr_filt[i]))
#		pfs_comb_dom[i] = list(reversed(pfs_comb_dom[i]))
#		
#		pfs_sel_comb[i] = list(reversed(pfs_sel_comb[i]))
#		pfs_sel_own[i] = list(reversed(pfs_sel_own[i]))
#		pfs_sel_other[i] = list(reversed(pfs_sel_other[i]))

# fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2,3)
figb, ((ax1b, ax2b, ax3b, ax7b), (ax4b, ax5b, ax6b, ax8b)) = plt.subplots(2,4, figsize=(25, 13))

#axarr = [ax1, ax2, ax3, ax4, ax5, ax6]
axarrb = [ax1b, ax2b, ax3b, ax4b, ax5b, ax6b, ax7b, ax8b]
# print pfs_by_env

vals = [pfs_by_env, pfs_pfr_filt, pfs_comb_dom, pfs_sel_comb, pfs_sel_own, pfs_sel_other, pfs_pcs, pfs_pcs_filt]
print 'WARNING: FIRST TWO MEASURES use env-wise filters'
# vals = [pfs_pcs, pfs_pcs_filt, pfs_comb_dom, pfs_sel_comb, pfs_sel_own, pfs_sel_other]

labels = ['PFS by environment (only RESP,SPARS,COH filters)', 'PFS by environment with firing rate filters', 'PFS of combined map by dominant environment', 'PFS of selective cells, combined map', 'PFS of selective cells in own environment', 'PFS of selective cells, other environment', 'PFS of own map of place cells in every environment', 'PFS of own map of place cells in every environent + firing rate filters']

bw = 0.2

ps = []
ps_mw = []
sts_mw = []
ps_ks = []

print 'Total cells: %d' % celltot

# dump values
#for MEAS in [0,1,4,7]:
for MEAS in [7]:
	fvalout = open('PFS_VALS%d_TARG%s.out' % (MEAS, OUTSUF), 'w')
	for v in vals[MEAS][0]:
		fvalout.write(str(v)+ '\n')
	fvalout.close()
	fvalout = open('PFS_VALS%d_CON%s.out' % (MEAS, OUTSUF), 'w')
	for v in vals[MEAS][1]:
		fvalout.write(str(v)+ '\n')
	fvalout.close()

# write list of indices
indall_c = map(int, indall_c)
indall_t = map(int, indall_t)
np.savetxt('INDALL_CON%s.txt' % OUTSUF, indall_c, fmt = '%d')
np.savetxt('INDALL_TARG%s.txt' % OUTSUF, indall_t, fmt = '%d')



for i in range(8):
	print '%s : %d/%d values' % (labels[i], len(vals[i][0]), len(vals[i][1]))

	# print vals[i]
	v1 = vals[i][0]
	v2 = vals[i][1]

	#axarr[i].scatter(range(len(v1)), [ 2*(v1[j]-v2[j])/(v1[j]+v2[j]) for j in range(len(vals[i]))])	
	#axarr[i].plot([0, len(v1)], [0, 0])

	v1 = np.array(v1)
	v2 = np.array(v2)
	ind1 = ~np.isnan(v1)
	ind2 = ~np.isnan(v2)
	#p=ttest_ind(v1[ind1], v2[ind2])[1]
	p_ks = ks_2samp(v1[ind1], v2[ind2])[1]
	# ps.append(p)
	ps_ks.append(p_ks)

	(st_mw, p_mw) = mannwhitneyu(v1[ind1], v2[ind2])
	ps_mw.append(p_mw)
	sts_mw.append(st_mw)
	pw = 0 #if i > 0 else wilcoxon(v1[ind1], v2[ind2])[1]

	ps.append(p_mw)

	axarrb[i].set_title(labels[i] + ' %.3f/%.3f' % (p_ks, pw))
	#axarrb[i].bar([0,1], [np.mean(v1[ind1]), np.mean(v2[ind2])], width = bw)
	axarrb[i].bar([0], [np.mean(v1[ind1])], width = bw)
	axarrb[i].bar([1], [np.mean(v2[ind2])], width = bw, color='r')
	axarrb[i].legend(['Target', 'Control'], loc='best')
	axarrb[i].errorbar([0+bw/2], [np.mean(v1[ind1])], yerr=[np.std(v1[ind1])/sqrt(sum(ind1))], color='black', linewidth=3)
	axarrb[i].errorbar([1+bw/2], [np.mean(v2[ind2])], yerr=[np.std(v2[ind2])/sqrt(sum(ind2))], color='black', linewidth=3)

	#axarrb[i].errorbar([0+bw/2, 1+bw/2], [np.mean(v1[ind]), np.mean(v2[ind])], yerr=[np.std(v1[ind])/sqrt(sum(ind)), np.std(v2[ind])/sqrt(sum(ind))])

#plt.suptitle(' '.join(argv[1:5]))
#plt.figure(fig.number)
plt.suptitle('%s: MINPFR: %s, MAXPFR: %s, MAX_OTHER_RATIO: %s, MINPFR 2ND SES: %s; MIN RESP: %s' % (argv[6], argv[1], argv[2], argv[3], argv[4], argv[5]))

if len(msgmissing) > 0:
	print 'WARNING! FOLLOWING FIELS ARE MISSING (SKIPPED): ' + msgmissing

# plt.show()

# OUTPUT
outpath = 'PFS_SUMMARY.out'
init = not os.path.isfile(outpath)

foutstat = open('PFS_VALS_STATS.txt', 'a')
foutstat.write(' '.join(argv[1:6]) + '\n')

fout = open(outpath, 'a')
if init:
	fout.write(' ' * 50 + '      1              2              3              4              5              6              7              8\n')
	#fout.write(' ' * 50 + '  1     2     3     4     5     6\n')
pstring = ' '.join(argv[1:6])
spaces = ' ' *(50-len(pstring))
fout.write(pstring + spaces)
i = 0
for p in ps:
	psg = psig(p)
	v0 = vals[i][0]
	v1 = vals[i][1]
	fout.write('%.2f%s%.2f|' % (np.nanmean(vals[i][0]), psg, np.nanmean(vals[i][1])))
	# mean std n mean std n p_ks p_mw
	foutstat.write('%f %f %d %f %f %d %f %f %f\n' % (np.nanmean(v0), np.nanstd(v0), len(v0), np.nanmean(v1), np.nanstd(v1), len(v1), ps_ks[i], ps_mw[i], sts_mw[i]))
	i += 1

fout.write('\n')
fout.close()
