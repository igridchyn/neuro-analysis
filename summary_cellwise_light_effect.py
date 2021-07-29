#!/usr/bin/env python2

import os
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from iutils import *
from scipy.stats import ttest_rel, ttest_ind, wilcoxon, spearmanr, pearsonr
from math import sqrt
import statsmodels.api as sm
from call_log import log_call

def resp_to_ind(sresp, vresp):
	if sresp == '0':
		indresp = np.array([True] * len(vresp))
		resp = 0
	else:
		if ':' in sresp:
			cpos = sresp.find(':')
			rmin = float(sresp[:cpos])
			rmax = float(sresp[cpos+1:])
			indresp = (vresp > rmin) & (vresp < rmax)
			# INVALID IN THIS CASE 
			resp = rmin
		elif sresp[0] == 'a':
			if sresp[1] == '-':
				resp = float(sresp[2:])
				indresp = np.abs(vresp) < resp
			else:
				resp = float(sresp[1:])
				indresp = np.abs(vresp) > resp
		elif sresp[0] == '-':
			resp = float(sresp)
			indresp = vresp < resp
		else:
			resp = float(sresp)
			indresp = vresp > resp

	return resp, indresp

if len(argv) < 9:
	print 'USAGE: (1)<file with list of directories> (2)<file name (has to be present in the directory)> (3)<min firing rate> (4)<max firing rate> (5)<response> (6)<selectivity factor> (7)<output path> (8)<use mean : 0/1>'
	print 'Summarize (figures and tests) effects on cell firing rates and correlations by combining data from given files and applying filters'
	exit(0)

ld = log_call(argv)
pdic = parse_optional_params(argv[9:])

# 7 IF TRUE !
USEMEAN = int(argv[8]) * 7

# mode of correlating different reponse categories of cells
RESP2 = False
sresp2 = gdv(pdic, 'resp2', '')
if sresp2 != '':
	RESP2 = True
	
# by reading cellwise_light_output and coherence / sparsity files:
# form arrays of: correlations of rates before and after, rates before and after

dirlistpath = argv[1]
cleoutfile = argv[2]
minpfr = float(argv[3])
maxpfr = float(argv[4])
mincoh = 0.5
maxspars = 0.3
sresp = argv[5]
selfac = float(argv[6])
outpath = argv[7]

# to distinguish couple filtering logic - OR of inh/disinh ; AND for unaffected / all
UNAFF = ':' in sresp
print 'WARNING: USING %s LOGIC FOR RESPONSE COUPLES' % (['OR', 'AND'][UNAFF])

dirs = []
for line in open(dirlistpath):
	if len(line) > 1:
		dirs.append(line[:-1])
print '%d directories' % len(dirs)

# summary arrays: correlations and firing rates: target / control, before / after
frstargbef = []
frstargaft = []
frsconbef = []
frsconaft = []
targcorrs = []
concorrs = []

# all values
acle = []
acoh1 = []
acoh2 = []
aspars1 = []
aspars2 = []
aindtarg = []
aindcon = []

# before-after reactivation
bareactscon = []
bareactstarg = []

allcorrsbefcon = []
allcorrsaftcon = []
allcorrsbeftarg = []
allcorrsafttarg = []

# all correlations - learning end control / target
allcorrs_lend_con  = []
allcorrs_lend_targ = []
# all correlations - learning end control / target in the OTHER ENVIRONMENT
allcorrs_lend_con_in_targ  = []
allcorrs_lend_targ_in_con = []

# pass percentage and titles
passp = {'SP1':0, 'CH1':0, 'SP2':0, 'CH2':0, 'MIN1':0, 'MIN2':0, 'MAX1':0, 'MAX2':0, 'RESP':0, 'SEL':0}
celltot = 0

# mean correlations of population vectors
pcorr_con  = 0
pcorr_targ = 0
npcorr     = 0.0

# pre-sleep cofiring correlations : before and after
l_cc_pres_b_con = []
l_cc_pres_a_con = []
l_cc_pres_b_targ = []
l_cc_pres_a_targ = []

# cofiring correlations by response categories
l_cc_resp_b = []
l_cc_resp_a = []

# for comparing b/a vs end of learning, combined control + target, filtered by response
allcorrs_lend_both = []
l_cc_both_b = []
l_cc_both_a = []

for dr in dirs:
	print dr
	# read day data - cle output, coherences, sparsities
	cleout = []
	# read cle output : peak1, peak2, resp, rate before, rate after, sleep-wise rate, correlation of even-wise rates before and after
	for line in open(dr + '/' + cleoutfile):
		cleout.append([float(f) for f in line.split(' ')])
	cleout = np.array(cleout)
	print '%d cells in *.cle' % len(cleout)

	# read sparisites and coherences
	spars1 = np.array(read_float_list(dr + '/../sparsity_BS6_OT5_E1.txt'))
	spars2 = np.array(read_float_list(dr + '/../sparsity_BS6_OT5_E2.txt'))
	coh1 = np.array(read_float_list(dr + '/../coherence_BS6_OT5_E1.txt'))
	coh2 = np.array(read_float_list(dr + '/../coherence_BS6_OT5_E2.txt'))
	spars1nl = np.array(read_float_list(dr + '/../sparsity_BS6_OT5_E1_NL1.txt'))
	spars2nl = np.array(read_float_list(dr + '/../sparsity_BS6_OT5_E2_NL1.txt'))
	coh1nl = np.array(read_float_list(dr + '/../coherence_BS6_OT5_E1_NL1.txt'))
	coh2nl = np.array(read_float_list(dr + '/../coherence_BS6_OT5_E2_NL1.txt'))

	# collect into the arrays
	acoh1.extend(coh1)
	acoh2.extend(coh2)
	aspars1.extend(spars1)
	aspars2.extend(spars2)
	if len(acle) == 0:
		acle = cleout
	else:
		acle = np.concatenate((acle, cleout))
	
	# filter by: sparsity, coherence, firing rate, response
	
	celltot += float(len(spars1))
	
	#ind1= ((spars1 < maxspars)  & (coh1 > mincoh) | (spars1nl < maxspars) & (coh1nl > mincoh)) & (cleout[:,0] > minpfr)&(cleout[:,0] < maxpfr)
	#ind2= ((spars2 < maxspars)  & (coh2 > mincoh) | (spars2nl < maxspars) & (coh2nl > mincoh)) & (cleout[:,1] > minpfr)&(cleout[:,1] < maxpfr)
	print 'WARNING: USING MEAN RATES!'
	ind1= ((spars1 < maxspars)  & (coh1 > mincoh) | (spars1nl < maxspars) & (coh1nl > mincoh)) & (cleout[:,USEMEAN] > minpfr)&(cleout[:,USEMEAN] < maxpfr)
	ind2= ((spars2 < maxspars)  & (coh2 > mincoh) | (spars2nl < maxspars) & (coh2nl > mincoh)) & (cleout[:,USEMEAN+1] > minpfr)&(cleout[:,USEMEAN+1] < maxpfr)

	# count passing cells
	passp['SP1'] += np.sum((spars1 < maxspars) | (spars1nl < maxspars))
	passp['SP2'] += np.sum((spars2 < maxspars) | (spars2nl < maxspars))
	passp['CH1'] += np.sum((coh1 > mincoh) | (coh1nl > mincoh))
	passp['CH2'] += np.sum((coh2 > mincoh) | (coh2nl > mincoh))

	passp['MIN1'] += np.sum(cleout[:,USEMEAN]   > minpfr)
	passp['MIN2'] += np.sum(cleout[:,USEMEAN+1] > minpfr)
	passp['MAX1'] += np.sum(cleout[:,USEMEAN]   < maxpfr)
	passp['MAX2'] += np.sum(cleout[:,USEMEAN+1] < maxpfr)

	# swap + other vars
	full = '_FULL' if os.path.isdir(dr + '/../8pres_FULL') else ''
	apath = dr + '/../about.txt'
        for line in open(apath):
                if line.startswith('swap'):
                        swap = int(line.split(' ')[-1])
                        print 'Swap ', swap
		if line.startswith('animal'):
			animal = line.split(' ')[-1][:-1]
		if line.startswith('date'):
			day = line.split(' ')[-1][2:-1]

	# 7REG responses
	print 'WARNING: 7reg respones are used for fitlering; JUN26 IF AVAIL!'
	# print 'WARNING: RESPONSES LOADED FROM 13SSI'

	j26 = dr + '/../7reg%s/pulses.timestamps.responses' % full
	#if os.path.isfile(j26):
	#	regresp = read_float_array(j26)
	#else:
	regresp = read_float_array(dr + '/../7reg%s/pulses.timestamps.responses' % full)
	#regresp = read_float_array(dr + '/../13ssi%s/inh.timestamps.responses' % full)

	# RESPONSE filter :
	#	-  : no filtering
	#	a- : abs less
	# 	a : abs more
	# 	- <positive number> : less than <positive number>
	# 	<positive value> : more than <positive value>

	vresp = regresp
	#vresp = cleout[:,2]

	resp, indresp = resp_to_ind(sresp, vresp)
	LIMRESP = resp

	if RESP2:
		resp2, indresp2 = resp_to_ind(sresp2, vresp)

	# LATER - OR logic	
	#ind1 = ind1 & indresp
	#ind2 = ind2 & indresp

	passp['RESP'] += np.sum(indresp)

	print 'Number of cells passing sparsity/coherence/rate/response filters in E1: ', np.sum(ind1)
	print 'Number of cells passing sparsity/coherence/rate/response filters in E2: ', np.sum(ind2)
	
	# selectivity filter on top !
	if selfac < 0:
		indtarg = ind2 #& (cleout[:,swap] > (selfac * cleout[:,1-swap]))
		indcon = ind1  #& (cleout [:,1-swap] > (selfac * cleout[:,swap]))
	else:
		#indtarg = ind2 & ((cleout[:,swap] > (selfac * cleout[:,1-swap]))  )#| np.isnan(cleout[:,1-swap]))
		#indcon = ind1  & ((cleout [:,1-swap] > (selfac * cleout[:,swap])) )#| np.isnan(cleout[:,swap]))
		# MEANRATES
		indtarg = ind2 & ((cleout[:,USEMEAN + swap] > (selfac * cleout[:,USEMEAN + 1 - swap]))  | np.isnan(cleout[:,USEMEAN + 1 - swap]))
		indcon = ind1  & ((cleout [:,USEMEAN + 1 - swap] > (selfac * cleout[:,USEMEAN + swap])) | np.isnan(cleout[:,USEMEAN + swap]))

	passp['SEL'] += np.sum((cleout[:,USEMEAN] > (selfac * cleout[:,USEMEAN + 1])) | (cleout[:,USEMEAN + 1] > (selfac * cleout[:,USEMEAN])) )#| np.isnan(cleout[:,USEMEAN]) | np.isnan(cleout[:,USEMEAN+1]))

	# read mean population vector correlations
	PCORR = os.path.isfile(dr + '/' + cleoutfile + '.pcorr')
	if PCORR:
		fpcorr = open(dr + '/' + cleoutfile + '.pcorr')
		pline = fpcorr.readline()
		[p1, p2, n] = [float(f) for f in pline.split(' ')]
		pcorrs = [p1, p2]
		pcorr_targ += pcorrs[swap]     * n
		pcorr_con  += pcorrs[1 - swap] * n
		npcorr += n

	# update grand array of filtered cells
	aindtarg.extend(indtarg & indresp)
	aindcon.extend(indcon & indresp)

	# DEBUG
	print 'CONTROL IND', np.where((indcon & indresp &  ~np.isnan(cleout[:,3]) & ~np.isnan(cleout[:,4])& ~np.isinf(cleout[:,3]) & ~np.isinf(cleout[:,4])) == True)[0]
	print 'TARG IND', np.where((indtarg & indresp &  ~np.isnan(cleout[:,3]) & ~np.isnan(cleout[:,4])& ~np.isinf(cleout[:,3]) & ~np.isinf(cleout[:,4])) == True)[0]

	# load waking cofiring correlations
	print os.getcwd()
	if swap:
		cc_lend_con = np.loadtxt(dr + '/../9l%s/%s_%s_9l.NOSB_ST4_TL5.corr_e1' % (full, animal, day))
		cc_lend_targ = np.loadtxt(dr + '/../9l%s/%s_%s_9l.NOSB_ST4_TL5.corr_e2' % (full, animal, day))
	else:
		cc_lend_targ = np.loadtxt(dr + '/../9l%s/%s_%s_9l.NOSB_ST4_TL5.corr_e1' % (full, animal, day))
		cc_lend_con = np.loadtxt(dr + '/../9l%s/%s_%s_9l.NOSB_ST4_TL5.corr_e2' % (full, animal, day))

	[cc_pres_b, cc_pres_a] = np.load(dr + '/../8pres%s/sync.corrmats.corrmats.npy' % full)

	# load corrmats and compute reactivation = co-firing correlation
	corrmatpath = dr + '/' + cleoutfile + '.corrmats.npy'
	[corrsb, corrsa] = np.load(corrmatpath)
	lcorrsbcon = []
	lcorrsacon = []
	lcorrsbtarg = []
	lcorrsatarg = []
	# correlations in presleep - before and after
	print 'WARNING: OR for INHIBITION CC FILTER'

	# print 'WARNING: couples from joint lists collected, environment corresponds to inh / ninh'

	for i in range(corrsa.shape[0]):
		for j in range(i):
			# or-logic is also ok for ALL cells
			resppass = (indresp[i] and indresp[j]) if UNAFF else (indresp[i] or indresp[j])

			# control cells
			if resppass and indcon[j] and indcon[i] and ~np.isnan(corrsb[i,j]) and ~np.isnan(corrsa[i,j]):
			# mixed couples of control and target
			#if resppass and (indcon[j] or indtarg[j]) and (indcon[i] or indtarg[i]) and ~np.isnan(corrsb[i,j]) and ~np.isnan(corrsa[i,j]):
				lcorrsbcon.append(corrsb[i,j])
				lcorrsacon.append(corrsa[i,j])

				#if 'ninh' in cleoutfile: # OR IF NO MIXED COUPLES - NORMAL MODE
				allcorrs_lend_con.append(cc_lend_con[i,j])
				allcorrs_lend_con_in_targ.append(cc_lend_targ[i,j])
				#else:
				#	allcorrs_lend_con.append(cc_lend_targ[i,j])
				#	allcorrs_lend_con_in_targ.append(cc_lend_con[i,j])

				l_cc_pres_b_con.append(cc_pres_b[i,j])
				l_cc_pres_a_con.append(cc_pres_a[i,j])

			# target cells - not used if mixed couples are considered
			if resppass and indtarg[j] and indtarg[i] and ~np.isnan(corrsb[i,j]) and ~np.isnan(corrsa[i,j]):
				lcorrsbtarg.append(corrsb[i,j])
				lcorrsatarg.append(corrsa[i,j])
				allcorrs_lend_targ.append(cc_lend_targ[i,j])
				allcorrs_lend_targ_in_con.append(cc_lend_con[i,j])
				l_cc_pres_b_targ.append(cc_pres_b[i,j])
				l_cc_pres_a_targ.append(cc_pres_a[i,j])

			if RESP2:
				if (indresp[i] and indresp2[j]) and (indcon[j] or indtarg[i]) and (indcon[i] or indtarg[j]) and ~np.isnan(corrsb[i,j]) and ~np.isnan(corrsa[i,j]):
					l_cc_resp_b.append(corrsb[i,j])
					l_cc_resp_a.append(corrsa[i,j])

			# common list - control + target
			# ! OR LOGIC FOR INH !
			# ... realised that cofiring correlations in waking are calculated separately in control and target, so can just combine both lists and calculate correlations
			#if (indresp[i] or indresp[j]) and (indtarg[j] or indcon[j]) and (indtarg[i] or indcon[i]) and ~np.isnan(corrsb[i,j]) and ~np.isnan(corrsa[i,j]) and ~np.isnan(cc_lend_targ[i,j]):
			#	allcorrs_lend_both.append()
			#	l_cc_both_b.append()
			#	l_cc_both_a.append()


	lcorrsacon = np.array(lcorrsacon)
	lcorrsbcon = np.array(lcorrsbcon)
	lcorrsatarg = np.array(lcorrsatarg)
	lcorrsbtarg = np.array(lcorrsbtarg)

	if sum(indcon) > 1:
		bareactscon.append(np.corrcoef(lcorrsbcon, lcorrsacon)[0,1])
	else:
		print 'NO CELLS or 1 CELL'
	if sum(indtarg) > 1:
		bareactstarg.append(np.corrcoef(lcorrsbtarg, lcorrsatarg)[0,1])
	else:
		print 'NO CELLS or 1 CELL in TARGET'
	#print bareacts

	allcorrsbefcon.extend(lcorrsbcon)
	allcorrsaftcon.extend(lcorrsacon)
	allcorrsbeftarg.extend(lcorrsbtarg)
	allcorrsafttarg.extend(lcorrsatarg)


#=========================================================== SUMMARIZE ================================================================

# WRITTEN LATER !
if npcorr > 0:
	print '		MEASURE 2: MEAN POPULATION VECTOR CORRELATIONS: %.2f / %.2f' % (pcorr_con / npcorr, pcorr_targ / npcorr)

print 'FILTER PASSING:'
for k in passp:
	print '%s : %.1f' % (k, passp[k] / celltot * 100)

print 'Mean reactivation CON / TARG: %.2f / %.2f' % (np.mean(bareactscon), np.mean(bareactstarg))
print 'Std reactivation CON / TARG: %.2f / %.2f' % (np.std(bareactscon), np.std(bareactstarg))

# write correlations to file
foutcorc = open(outpath + '.corrs.con', 'w')
for v in bareactscon:
	foutcorc.write('%f\n' % v)
foutcort = open(outpath + '.corrs.targ', 'w')
for v in bareactstarg:
	foutcort.write('%f\n' % v)

aindtarg = np.array(aindtarg)
aindcon = np.array(aindcon)

# rate non-nan
rnindtarg = aindtarg & ~np.isnan(acle[:,3]) & ~np.isnan(acle[:,4])& ~np.isinf(acle[:,3]) & ~np.isinf(acle[:,4])
rnindcon = aindcon & ~np.isnan(acle[:,3]) & ~np.isnan(acle[:,4]) & ~np.isinf(acle[:,3]) & ~np.isinf(acle[:,4])

# DEBUG
print 'Control rates before:'
print acle[rnindcon, 3]
print 'Target rates before:'
print acle[rnindtarg, 3]

# DEBUG - see distribution of rates
#plt.hist(acle[rnindcon, 3], 20)
#plt.hist(np.log(acle[rnindcon, 3]), 20)
#plt.show()

# correlation of mean firing rates before and after : control vs. target

bacorrcon = np.corrcoef(acle[rnindcon, 3], acle[rnindcon, 4])[0,1]
bacorrtarg = np.corrcoef(acle[rnindtarg, 3], acle[rnindtarg, 4])[0,1]
p_bacorrcon = pearsonr(acle[rnindcon, 3], acle[rnindcon, 4])[1]
p_bacorrtarg = pearsonr(acle[rnindtarg, 3], acle[rnindtarg, 4])[1]
print '		MEASURE 4: CORRELATION OF MEAN FIRING RATES BEFORE AND AFTER: CONTROL / TARGET: %.2f / %.2f' % (bacorrcon, bacorrtarg)
print 'p-values of correlations of mean rates : control, target:', p_bacorrcon, p_bacorrtarg

# correlation of co-firings of cells in 2 response categories
respcorr = np.corrcoef(l_cc_resp_b, l_cc_resp_a)[0, 1]

foutcombcorrs = open(outpath + '.combcorrs', 'w')

# LINE 1 - correlations of before / after by environment
combcorrscon = np.corrcoef(allcorrsbefcon, allcorrsaftcon)[0,1]
combcorrstarg = np.corrcoef(allcorrsbeftarg, allcorrsafttarg)[0,1]
#combcorrscon = spearmanr(allcorrsbefcon, allcorrsaftcon)[0]
#combcorrstarg = spearmanr(allcorrsbeftarg, allcorrsafttarg)[0]
print 'Combined correalations: CON / TARG : %.2f / %.2f      (%d/%d)' % (combcorrscon, combcorrstarg, len(allcorrsbefcon), len(allcorrsbeftarg))
foutcombcorrs.write('%f %f %d %d\n' % (combcorrscon, combcorrstarg, len(allcorrsbefcon), len(allcorrsbeftarg)))

# LINE 2 -  MEASURE 3 - mean co-firings before and after control / target
foutcombcorrs.write('%f %f %f %f\n' % (np.mean(allcorrsbefcon), np.mean(allcorrsaftcon), np.mean(allcorrsbeftarg), np.mean(allcorrsafttarg)))
# LINE 3 - correlations of mean rates before and after + p-values
foutcombcorrs.write('%f %f %d %d %f %f\n' % (bacorrcon, bacorrtarg, np.sum(rnindcon), np.sum(rnindtarg), p_bacorrcon, p_bacorrtarg))

allcorrs_lend_con = np.array(allcorrs_lend_con)
allcorrs_lend_targ = np.array(allcorrs_lend_targ)
allcorrsaftcon = np.array(allcorrsaftcon)
allcorrsbefcon = np.array(allcorrsbefcon)
allcorrsafttarg = np.array(allcorrsafttarg)
allcorrsbeftarg = np.array(allcorrsbeftarg)
allcorrs_lend_con_in_targ = np.array(allcorrs_lend_con_in_targ)
allcorrs_lend_targ_in_con = np.array(allcorrs_lend_targ_in_con)

# partial correlations of before / after given waking
#con_nan = ~np.isnan(allcorrsbefcon) & ~np.isnan(allcorrs_lend_con)
#targ_nan = ~np.isnan(allcorrsbeftarg) & ~np.isnan(allcorrs_lend_targ)
#lm_bcon = sm.OLS(allcorrsbefcon[con_nan], allcorrs_lend_con[con_nan])
#lm_acon = sm.OLS(allcorrsaftcon[con_nan], allcorrs_lend_con[con_nan])
#lm_btarg = sm.OLS(allcorrsbeftarg[targ_nan], allcorrs_lend_targ[targ_nan])
#lm_atarg = sm.OLS(allcorrsafttarg[targ_nan], allcorrs_lend_targ[targ_nan])
#lm_bcon_res = lm_bcon.fit().resid
#lm_acon_res = lm_acon.fit().resid
#lm_btarg_res = lm_btarg.fit().resid
#lm_atarg_res = lm_atarg.fit().resid
#combcorrscon_part_lend = np.corrcoef(lm_acon_res, lm_bcon_res)[0,1]
#combcorrstarg_part_lend = np.corrcoef(lm_atarg_res, lm_btarg_res)[0,1]

combcorrscon_part_lend =  partial_correlation(allcorrsbefcon, allcorrsaftcon, allcorrs_lend_con)
combcorrstarg_part_lend = partial_correlation(allcorrsbeftarg, allcorrsafttarg, allcorrs_lend_targ)

# line 4
foutcombcorrs.write('%f %f %d %d\n' % (combcorrscon_part_lend, combcorrstarg_part_lend, len(allcorrsbefcon), len(allcorrsbeftarg)))

nind_lend_con  = ~np.isnan(allcorrs_lend_con)
nind_lend_targ = ~np.isnan(allcorrs_lend_targ)
# correlations with waking cofirings - before and after light for control / target
cc_lend_bef_con = np.ma.corrcoef(allcorrs_lend_con[nind_lend_con], allcorrsbefcon[nind_lend_con])[0,1]
cc_lend_aft_con = np.ma.corrcoef(allcorrs_lend_con[nind_lend_con], allcorrsaftcon[nind_lend_con])[0,1]
cc_lend_bef_targ = np.ma.corrcoef(allcorrs_lend_targ[nind_lend_targ], allcorrsbeftarg[nind_lend_targ])[0,1]
cc_lend_aft_targ = np.ma.corrcoef(allcorrs_lend_targ[nind_lend_targ], allcorrsafttarg[nind_lend_targ])[0,1]
# line 5
foutcombcorrs.write('%f %f %f %f %d %d %d %d\n' % (cc_lend_bef_con, cc_lend_aft_con, cc_lend_bef_targ, cc_lend_aft_targ, len(allcorrsbefcon), len(allcorrsbefcon), len(allcorrsbeftarg), len(allcorrsbeftarg)))

# partial correlations of before / after given pre-sleep correlations before
l_cc_pres_a_targ = np.array(l_cc_pres_a_targ)
l_cc_pres_b_targ = np.array(l_cc_pres_b_targ)
l_cc_pres_a_con = np.array(l_cc_pres_a_con)
l_cc_pres_b_con = np.array(l_cc_pres_b_con)

# LINE 6 - PARTIAL CORRELATIONS GIVE PRE-SLEEP - BEFORE OR AFTER - defined below
partcor_pres_con = partial_correlation(allcorrsbefcon, allcorrsaftcon, l_cc_pres_a_con)
partcor_pres_targ = partial_correlation(allcorrsbeftarg, allcorrsafttarg, l_cc_pres_a_targ)
foutcombcorrs.write('%f %f %d %d\n' % (partcor_pres_con, partcor_pres_targ, len(allcorrsbefcon), len(allcorrsbeftarg)))

# WRITE MEASURE 2
# line 7
if npcorr == 0:
	npcorr = 1
	print 'WARNING: npcorr=0, set to 1'
foutcombcorrs.write('%f %f %d %d\n' % (pcorr_con / npcorr, pcorr_targ / npcorr, npcorr, npcorr))

# line 8 - correlations of response-grouped co-firings
foutcombcorrs.write('%f %d\n' % (respcorr, len(l_cc_resp_a)))

# CORRELATIONS OF COMBINED LISTS OF COFIRINGS FOR CONTROL / TARGET - FILTERED BY RESP ONLY !
lend_comb = np.concatenate((allcorrs_lend_con, allcorrs_lend_targ))
nind_lc = ~np.isnan(lend_comb) & ~np.isinf(lend_comb)
cc_lend_bef = np.ma.corrcoef(lend_comb[nind_lc], np.concatenate((allcorrsbefcon, allcorrsbeftarg))[nind_lc])[0,1]
cc_lend_aft = np.ma.corrcoef(lend_comb[nind_lc], np.concatenate((allcorrsaftcon, allcorrsafttarg))[nind_lc])[0,1]

# line 9
foutcombcorrs.write('%f %f %d %d\n' % (cc_lend_bef, cc_lend_aft, len(allcorrsbefcon) + len(allcorrsbeftarg), len(allcorrsaftcon) + len(allcorrsafttarg)))

# line 10 - write params in the end
foutcombcorrs.write(' '.join(argv) + '\n')

# line 11 - cerrelation of combined lists of control and target cells co-firings before/after light VS. co-firing of cell couple's in opposite environment
lend_comb_opposite = np.concatenate((allcorrs_lend_con_in_targ, allcorrs_lend_targ_in_con))
nind_lc_op = ~np.isnan(lend_comb_opposite) & ~np.isinf(lend_comb_opposite)
cc_lend_bef_op = np.ma.corrcoef(lend_comb_opposite[nind_lc_op], np.concatenate((allcorrsbefcon, allcorrsbeftarg))[nind_lc_op])[0,1]
cc_lend_aft_op = np.ma.corrcoef(lend_comb_opposite[nind_lc_op], np.concatenate((allcorrsaftcon, allcorrsafttarg))[nind_lc_op])[0,1]
foutcombcorrs.write('%f %f %d %d\n' % (cc_lend_bef_op, cc_lend_aft_op, np.sum(nind_lc_op), np.sum(nind_lc_op)))

# line 12 - correlations of before/after coifirings with end-of-learning co-firings in the other environment - as a control !
# VALID ONLY IF COUPLES FROM JOINT LIST ARE FILTERED
nind_ct = ~np.isnan(allcorrs_lend_con_in_targ)
nind_tc = ~np.isnan(allcorrs_lend_targ_in_con)
cc_lend_targ_bef_con = np.ma.corrcoef(allcorrs_lend_con_in_targ[nind_ct], allcorrsbefcon[nind_ct])[0,1]
cc_lend_targ_aft_con = np.ma.corrcoef(allcorrs_lend_con_in_targ[nind_ct], allcorrsaftcon[nind_ct])[0,1]
cc_lend_con_bef_targ = np.ma.corrcoef(allcorrs_lend_targ_in_con[nind_tc], allcorrsbeftarg[nind_tc])[0,1]
cc_lend_con_aft_targ = np.ma.corrcoef(allcorrs_lend_targ_in_con[nind_tc], allcorrsafttarg[nind_tc])[0,1]
foutcombcorrs.write('%f %f %f %f %d %d %d %d\n' % (cc_lend_targ_bef_con, cc_lend_targ_aft_con, cc_lend_con_bef_targ, cc_lend_con_aft_targ, len(allcorrsbefcon), len(allcorrsbefcon), len(allcorrsbeftarg), len(allcorrsbeftarg)))

# lien 13 (=line 5 partial) - correlations of b/a with waking - before and after light for control / target - partial by pre-sleep
nind_pres_con = ~np.isnan(l_cc_pres_a_con) & ~np.isnan(l_cc_pres_b_con)
nind_pres_targ = ~np.isnan(l_cc_pres_a_targ) & ~np.isnan(l_cc_pres_b_targ)
nind_lend_con  = ~np.isnan(allcorrs_lend_con) & nind_pres_con
nind_lend_targ = ~np.isnan(allcorrs_lend_targ) & nind_pres_targ
cc_lend_bef_con = np.ma.corrcoef(allcorrs_lend_con[nind_lend_con], allcorrsbefcon[nind_lend_con])[0,1]
cc_lend_aft_con = np.ma.corrcoef(allcorrs_lend_con[nind_lend_con], allcorrsaftcon[nind_lend_con])[0,1]
cc_lend_bef_targ = np.ma.corrcoef(allcorrs_lend_targ[nind_lend_targ], allcorrsbeftarg[nind_lend_targ])[0,1]
cc_lend_aft_targ = np.ma.corrcoef(allcorrs_lend_targ[nind_lend_targ], allcorrsafttarg[nind_lend_targ])[0,1]
foutcombcorrs.write('%f %f %f %f %d %d %d %d\n' % (cc_lend_bef_con, cc_lend_aft_con, cc_lend_bef_targ, cc_lend_aft_targ, len(allcorrsbefcon), len(allcorrsbefcon), len(allcorrsbeftarg), len(allcorrsbeftarg)))

# =========================================================== PLOTTING ====================================================================
# ! reponce deciles - INVALID FOR ABSOLUTE VALUE FILTER !
if sresp[0] == '-':
	rdeciles = np.percentile(acle[acle[:,2] < LIMRESP,2], list(np.arange(0,101,10)))
else:
	rdeciles = np.percentile(acle[acle[:,2] > LIMRESP,2], list(np.arange(0,101,10)))
print 'RDECILES', rdeciles

SCATTER = False

if SCATTER:
    	if sresp[0] == 'a':
               if sresp[1] == '-':
                       indresp = np.abs(acle[:,2]) < resp
               else:
                       indresp = np.abs(acle[:,2]) > resp
        elif sresp[0] == '-':
               indresp = acle[:,2] < resp
        else:
               indresp = acle[:,2] > resp
        aindtarg = aindtarg & indresp
        aindcon = aindcon & indresp
	frstargbef = acle[aindtarg,3]
	frstargaft = acle[aindtarg,4]
	frsconbef = acle[aindcon,3]
	frsconaft = acle[aindcon,4]
	targcorrs = acle[aindtarg,6]
	concorrs = acle[aindcon,6]
	size = 10
	plt.scatter(frsconbef, frsconaft, s=size)
	plt.scatter(frstargbef, frstargaft, color = 'r', s=size)
	plt.legend(['CONTROL', 'TARGET'])
	rmax = 7
	plt.gca().set_xlim([0, rmax])
	plt.gca().set_ylim([0, rmax])
	#plt.suptitle('MINPFR %.1f, MAXPFR %.1f, COH %.2f\n SPARS %.2f SELECIVITY %.1f, %s' % (minpfr, maxpfr, mincoh, maxspars, selfac, cleoutfile), fontsize = 20)
	plt.suptitle('MIN MFR %.1f, MAX MFR %.1f, COH %.2f\n SPARS %.2f SELECIVITY %.1f, %s' % (minpfr, maxpfr, mincoh, maxspars, selfac, cleoutfile), fontsize = 20)
	plt.xlabel('Firing rate before')
	plt.ylabel('Firing rate after')
	plt.show()
	exit(0)

# single RATE SCORES plot
SINGLE = False

if not SINGLE:
	figb, ((ax1b, ax2b, ax3b)) = plt.subplots(1,3, figsize=(12, 6))
	axarrb = [ax1b, ax2b, ax3b]
else:
	figb, ((ax1b)) = plt.subplots(1,1, figsize=(4, 6))
	axarrb = [ax1b]
	
oaindtarg = aindtarg
oaindcon = aindcon

maxmeanrate = 0
pstr = ['p = '] * 3

fout = open(outpath, 'w')

for pi in range(len(rdeciles)):
	# absolute value filter : a- : abs less, a : abs more, -<positive number> : less than <positive number>; <positive value> : more than
	resp = rdeciles[pi]

	if sresp == '0':
                indresp = np.array([True] * len(acle[:,2]))
                resp = 0
        else:
                if ':' in sresp:
                        cpos = sresp.find(':')
                        rmin = float(sresp[:cpos])
                        rmax = float(sresp[cpos+1:])
                        indresp = (acle[:,2] > rmin) & (acle[:,2] < rmax)
                        # INVALID IN THIS CASE 
                        resp = rmin
		elif sresp[0] == 'a':
		       if sresp[1] == '-':
			       indresp = np.abs(acle[:,2]) < resp
		       else:
			       indresp = np.abs(acle[:,2]) > resp
		elif sresp[0] == '-':
		       indresp = acle[:,2] < resp
		else:
		       indresp = acle[:,2] > resp

	aindtarg = oaindtarg & indresp & ~np.isinf(acle[:,3])
	aindcon = oaindcon & indresp & ~np.isinf(acle[:,3])

	# DEBUG
	print 'INDCON  FINAL', np.where(aindcon  == True)[0]
	print 'INDTARG FINAL', np.where(aindtarg == True)[0]

	frstargbef = acle[aindtarg,3]
	frstargaft = acle[aindtarg,4]
	frsconbef = acle[aindcon,3]
	frsconaft = acle[aindcon,4]
	targcorrs = acle[aindtarg,6]
	concorrs = acle[aindcon,6]

	if len(frstargbef) == 0:
		print 'No values pssing all filters, create dummy arrays'
		# continue
		vals = [[[0],[1]],[[0],[1]],[[0], [1]]]

	#print 'Total values, CON/TARG: %d / %d' % (len(targcorrs), len(concorrs))
	#print 'CORRELATIONS OF MEAN RATES BEFORE-AFTER: CON / TARG %.3f / %.3f' % (np.corrcoef(np.array(frsconbef), np.array(frsconaft))[0,1], np.corrcoef(np.array(frstargbef), np.array(frstargaft))[0,1])
	else:
		vals = [[frsconbef, frstargbef], [frsconaft, frstargaft], [concorrs, targcorrs]]

	
	for i in range(3):
		for j in range(2):
			if len(vals[i][j]) == 0:
				vals[i][j] = [0]

	l1 = 'Firing rates before' if not SINGLE else 'RATE SCORES ((A-B)/(A+B))'
	labels = [l1, 'Firing rates after', 'Correlations of firing rates before and after']
	bw = 0.4
	ps = []

	for i in range(3):
		# print '%s : %d/%d values' % (labels[i], len(vals[i][0]), len(vals[i][1]))
		# print vals[i]i

		# NORMAL
		if not SINGLE:
			v1 = vals[i][0]
			v2 = vals[i][1]
		else:
			# SCORES - (DIFF)/(SUM)
			v1 = (vals[1][0]-vals[0][0])/(vals[1][0]+vals[0][0])
			v2 = (vals[1][1]-vals[0][1])/(vals[1][1]+vals[0][1])

		v1 = np.array(v1)
		v2 = np.array(v2)
		ind1 = ~np.isnan(v1) & ~np.isinf(v1)
		ind2 = ~np.isnan(v2) & ~np.isinf(v2)
		try:
			p=ttest_ind(v1[ind1], v2[ind2])[1]
		except:
			p = 1.0
		ps.append(p)
		pw = 0 #if i > 0 else wilcoxon(v1[ind1], v2[ind2])[1]

		pstr[i] += '%.2f '%p

		# string too long
		if pi == len(rdeciles) / 2:
			pstr[i] += '\n'

		# axarrb[i].set_title(labels[i] + '\n%.5f/%.2f' % (p, pw))
		axarrb[i].bar([2*pi], [np.mean(v1[ind1])], width = bw)
		axarrb[i].bar([2*pi+0.7], [np.mean(v2[ind2])], width = bw, color='r')
		if pi == 1:
			axarrb[i].legend(['CONTROL', 'TARGET'], loc='best')
		axarrb[i].errorbar([2*pi+bw/2], [np.mean(v1[ind1])], yerr=[np.std(v1[ind1])/sqrt(sum(ind1))], color='black', linewidth=3)
		axarrb[i].errorbar([2*pi+0.7+bw/2], [np.mean(v2[ind2])], yerr=[np.std(v2[ind2])/sqrt(sum(ind2))], color='black', linewidth=3)

		plt.sca(axarrb[i])
		nfs = 15
		plt.text(2*pi, np.mean(v1[ind1])/2, str(sum(ind1)), fontsize=nfs, color='green')
		plt.text(2*pi+0.7, np.mean(v2[ind2])/2, str(sum(ind2)), fontsize=nfs, color='green')
		
		if SINGLE:
			break

	sntarg = sqrt(len(frstargbef))
	sncon = sqrt(len(frsconbef))
	maxmeanrate = max(maxmeanrate, np.mean(frsconbef)+np.std(frsconbef)/sncon, np.mean(frsconaft)+np.std(frsconaft)/sncon, np.mean(frstargbef)+np.std(frstargbef)/sntarg, np.mean(frstargaft)+np.std(frstargaft)/sntarg)
	# write the results
	for i in range(3):
		#fout.write('%f %f %f %f %d %d\n' % (np.nanmean(vals[i][0]), np.nanmean(vals[i][1]), np.nanstd(vals[i][0]), np.nanstd(vals[i][1]), np.sum(~np.isnan(vals[i][0])), np.sum(~np.isnan(vals[i][1]))))

		n1 = np.sum(~np.isnan(vals[i][0]))
		fout.write('%d '% n1)
		for j in range(n1):
			if ~np.isnan(vals[i][0][j]):
				fout.write('%.4f '% vals[i][0][j])

		n2 = np.sum(~np.isnan(vals[i][1]))
		fout.write('%d '% n2)
		for j in range(n2):
			if ~np.isnan(vals[i][1][j]):
				fout.write('%.4f '% vals[i][1][j])
		fout.write('\n')

		if SINGLE:
			break

	# MEAN AND STD OF RATE SCORES
	cscore = np.array(vals[1][0])-np.array(vals[0][0])
	tscore = np.array(vals[1][1])-np.array(vals[0][1])
	fout.write('%f %f %f %f\n' % (np.nanmean(cscore), np.nanmean(tscore), np.nanstd(cscore), np.nanstd(tscore)))

#ax1b.set_ylim([0, maxmeanrate])
#ax2b.set_ylim([0, maxmeanrate])

for i in range(3):
	plt.sca(axarrb[i])
	plt.xticks([2*pi for pi in range(0,len(rdeciles),2)], ['%.2f'%rdeciles[j] for j in range(0,len(rdeciles),2)], fontsize=10)	
	axarrb[i].set_title(labels[i] + '\n%s' % pstr[i])
	plt.xlabel('Light response threshold')
	plt.grid()
	if SINGLE:
		break

# plt.suptitle('MINPFR %.1f, MAXPFR %.1f, COH %.2f SPARS %.2f SELECIVITY %.1f, %s' % (minpfr, maxpfr, mincoh, maxspars, selfac, cleoutfile), fontsize = 20)
plt.suptitle('MINPFR %.1f, MAXPFR %.1f, SEL %.1f, %s' % (minpfr, maxpfr, selfac, cleoutfile), fontsize = 15)

# plt.show()

