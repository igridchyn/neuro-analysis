#!/usr/bin/env python

from sys import argv
import numpy as np
from iutils import *
import os
from call_log import log_call
import warnings

if len(argv) < 16:
	print '(1)<values session 1 prefix> (2)<values session 2 prefix> (3)<firing rates s1 prefix> (4)<firing rates s2 prefix> (5)<responses> (6)<response threshold> (7)<pfs file> (8)<min pfr> (9)<max pfr> (10)<max PFS> (11)<min selectivity> (12)<pre-sleep co-firing matrix path> (13)<first trials corrmats or -> (14)<post co-firing matrix path> (15)<input suffix = output prefix>'
	exit(0)

argv[1] = '9l%{FULL}/%{animal}_%{day}_9l.' + argv[15] + argv[1]
argv[2] = '16l%{FULL}/%{animal}_%{day}_16l.' + argv[15] + argv[2]
argv[3] = '9l%{FULL}/%{animal}_%{day}_9l.' + argv[15] + argv[3]
argv[4] = '16l%{FULL}/%{animal}_%{day}_16l.' + argv[15]+ argv[4]
argv[12] = '8pres%{FULL}/' + argv[12]
argv[13] = '9f%{FULL}/%{animal}_%{day}_9f.' + argv[15] + argv[13]
argv[14] = '14post%{FULL}/%{animal}_%{day}_14post.' + argv[15] + argv[14]

argv = resolve_vars(argv)
# by meta
# dumpdir = log_call(argv)

print 'WARNING: RUNTIME WARNINGS DISABLED'
warnings.filterwarnings("ignore",category = RuntimeWarning)
warnings.filterwarnings("ignore",category = FutureWarning)

m1_e1 = np.loadtxt(argv[1] + 'e1')
m2_e1 = np.loadtxt(argv[2] + 'e1') 
m1_e2 = np.loadtxt(argv[1] + 'e2')
m2_e2 = np.loadtxt(argv[2] + 'e2') 
# PRESLEEP both before and after are present
mpres = np.load(argv[12])[0]
# PSOT
mpost_e1 = np.loadtxt(argv[14] + 'e1')
mpost_e2 = np.loadtxt(argv[14] + 'e2')


print 'mpres shape:', mpres.shape

FOUTPREF = argv[15]

if mpost_e1.shape != m1_e1.shape:
	nmpost_e1 = np.zeros(m1_e1.shape)
	nmpost_e2 = np.zeros(m1_e2.shape)
	d = mpost_e1.shape[0]
	nmpost_e1[:d, :d] = mpost_e1
	nmpost_e2[:d, :d] = mpost_e2
	mpost_e1 = nmpost_e1
	mpost_e2 = nmpost_e2

# first trials
FT = True
if argv[13] == '-':
	FT = False
else:
	fm1_e1 = np.loadtxt(argv[13] + 'e1')
	fm1_e2 = np.loadtxt(argv[13] + 'e2')
	# EXPAND IN CASE OF DIFFERENT SHAPE
	if fm1_e1.shape != m1_e1.shape:
		nfm1_e1 = np.zeros(m1_e1.shape)	
		nfm1_e2 = np.zeros(m1_e2.shape)	
		d = fm1_e1.shape[0]
		nfm1_e1[:d,:d] = fm1_e1
		nfm1_e2[:d,:d] = fm1_e2
		print 'WARNING: exmapded 9F arrays'
		fm1_e1 = nfm1_e1
		fm1_e2 = nfm1_e2

MINPFR = float(argv[8])
MAXPFR = float(argv[9])
REMAPMAX = float(argv[10])
SELMIN = float(argv[11])

if (m1_e1.shape != m2_e1.shape) or (m1_e2.shape != m2_e2.shape) or (m1_e1.shape != m1_e2.shape) or (m1_e1.shape != mpres.shape) or (FT and (m1_e1.shape != fm1_e1.shape)):
	print 'ERROR: different data size'
	print m1_e1.shape, m2_e1.shape, m1_e2.shape, m2_e2.shape, fm1_e1.shape if FT else ((0,0))
	exit(2)

# now these are loaded from the pfs file
#frs_s1 = np.loadtxt(argv[3])
#frs_s2 = np.loadtxt(argv[4])

responses = np.loadtxt(argv[5])
SRESP = argv[6]

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

# load sparsities / coherences
path = argv[3]
fspars1 = open(os.path.dirname(path) + '/../sparsity_BS6_OT5_E1.txt')
fcoh1 = open(os.path.dirname(path) + '/../coherence_BS6_OT5_E1.txt')
fspars2 = open(os.path.dirname(path) + '/../sparsity_BS6_OT5_E2.txt')
fcoh2 = open(os.path.dirname(path) + '/../coherence_BS6_OT5_E2.txt')
fspars1s2 = open(os.path.dirname(path) + '/../sparsity_BS6_OT5_E1_NL1.txt')
fcoh1s2 = open(os.path.dirname(path) + '/../coherence_BS6_OT5_E1_NL1.txt')
fspars2s2 = open(os.path.dirname(path) + '/../sparsity_BS6_OT5_E2_NL1.txt')
fcoh2s2 = open(os.path.dirname(path) + '/../coherence_BS6_OT5_E2_NL1.txt')
for line in fspars1:
                sparsity1.append(float(line))
                coherence1.append(float(fcoh1.readline()))
                sparsity2.append(float(fspars2.readline()))
                coherence2.append(float(fcoh2.readline()))
                sparsity1s2.append(float(fspars1s2.readline()))
                coherence1s2.append(float(fcoh1s2.readline()))
                sparsity2s2.append(float(fspars2s2.readline()))
                coherence2s2.append(float(fcoh2s2.readline()))
sparsity1 = np.array(sparsity1)
coherence1 = np.array(coherence1)
sparsity2 = np.array(sparsity2)
coherence2 = np.array(coherence2)
sparsity1s2 = np.array(sparsity1s2)
coherence1s2 = np.array(coherence1s2)
sparsity2s2 = np.array(sparsity2s2)
coherence2s2 = np.array(coherence2s2)

# read from pfs file: firing rates and pfs
pfss_e1 = []
pfss_e2 = []
peakfrs_e1_s0 = []
peakfrs_e2_s0 = []
peakfrs_e1_s1 = []
peakfrs_e2_s1 = []

print 'WARNING: using MEAN RATES isntead of peak rates for filtering'
fpfs = open(argv[7])
print 'WARNING: hard-coded PFS.out for remap filtering'
fpfs_remap = open('PFS_1_2_FTS_2.out')# open(argv[16])
for line in fpfs:
	vals = [float(w) for w in line.split(' ')]

	line_remap = fpfs_remap.readline()
	vals_remap = [float(w) for w in line_remap.split(' ')]
	# 1st or 2nd file ?
	pfss_e1.append(vals_remap[1])
	pfss_e2.append(vals_remap[2])

	# 3,4,5,6 for peak; 8,9,10,11 for mean
	peakfrs_e1_s0.append(vals[8])
	peakfrs_e2_s0.append(vals[9])
	peakfrs_e1_s1.append(vals[10])
	peakfrs_e2_s1.append(vals[11])
pfss_e1 = np.array(pfss_e1)
pfss_e2 = np.array(pfss_e2)
peakfrs_e1_s0 = np.array(peakfrs_e1_s0)
peakfrs_e1_s1 = np.array(peakfrs_e1_s1)
peakfrs_e2_s0 = np.array(peakfrs_e2_s0)
peakfrs_e2_s1 = np.array(peakfrs_e2_s1)

if REMAPMAX < 1.001:
	pfsind1 = pfss_e1 < REMAPMAX
	pfsind2 = pfss_e2 < REMAPMAX
else:
	pfsind1 = np.array([True] * len(pfss_e1))
	pfsind2 = np.array([True] * len(pfss_e2))

sparsind1 = ~np.isnan(sparsity1) & ~np.isnan(sparsity1s2) & ((sparsity1 < 0.3) | (sparsity1s2 < 0.3)) # 0.3
cohind1 = ~np.isnan(coherence1) & ~np.isnan(coherence1s2) & ((coherence1 > 0.5) | (coherence1s2 > 0.5)) # 0.5
sparsind2 = ~np.isnan(sparsity2) & ~np.isnan(sparsity2s2) & ((sparsity2 < 0.3) | (sparsity2s2 < 0.3)) # 0.3
cohind2 = ~np.isnan(coherence2) & ~np.isnan(coherence2s2) & ((coherence2 > 0.5) | (coherence2s2 > 0.5)) # 0.5

#selind = (peakfrs_e1_s1 > SELMIN * peakfrs_e2_s1) | (peakfrs_e2_s1 > SELMIN * peakfrs_e1_s1) | np.isnan(peakfrs_e1_s1) | np.isnan(peakfrs_e2_s1)
print 'WARNING: not selectivity filtering'
selind = np.array([True] * len(peakfrs_e1_s0))
#selind1 = selind
#selind2 = selind
selind1 = (peakfrs_e1_s1 > SELMIN * peakfrs_e2_s1) | np.isnan(peakfrs_e2_s1)
selind2 = (peakfrs_e2_s1 > SELMIN * peakfrs_e1_s1) | np.isnan(peakfrs_e1_s1)

REPS = 0.0001
if ':' in SRESP:
	cpos = SRESP.find(':')
	rt1 = float(SRESP[:cpos])
	rt2 = float(SRESP[cpos+1:])
	respind = (responses > rt1) & (responses < rt2)
else:
	resp_thold = float(SRESP)

	if abs(resp_thold) < REPS:
		respind = np.array([True] * len(responses))
		print 'WARNING: no response filter applied'
	elif resp_thold > 0:
		respind = responses > resp_thold 
	else:
		respind = responses < resp_thold

if SRESP == '0':
	resp_nodinh = np.array([True] * len(responses))
elif SRESP[0] == '-':
	resp_nodinh = responses < 0.6931
elif ';' not in SRESP:
	resp_nodinh = responses > -0.28768
else:
	resp_nodinh = respind	

#filtind1 = respind & sparsind1 & cohind1 & pfsind1 & selind1
#filtind2 = respind & sparsind2 & cohind2 & pfsind2 & selind2
#filtind1_allr = sparsind1 & cohind1 & pfsind1 & selind1 & resp_nodinh
#filtind2_allr = sparsind2 & cohind2 & pfsind2 & selind2 & resp_nodinh
# DOF : not using sparsity / coherence filters
#print 'WARINING: NO SPARSITY / COHERENCE FILTER, PAIRED CELL NO-DINH' 
filtind1 = respind & pfsind1 & selind1
filtind2 = respind & pfsind2 & selind2
filtind1_allr = pfsind1 & selind1 & resp_nodinh
filtind2_allr = pfsind2 & selind2 & resp_nodinh

ind_m8_1 = filtind1 	      & (peakfrs_e1_s0 < MAXPFR) & (peakfrs_e1_s0 > MINPFR)
ind_m8_2 = filtind2 	      & (peakfrs_e2_s0 > MINPFR) & (peakfrs_e2_s0 < MAXPFR)
ind_m8_1_allr = filtind1_allr & (peakfrs_e1_s0 < MAXPFR) & (peakfrs_e1_s0 > MINPFR)
ind_m8_2_allr = filtind2_allr & (peakfrs_e2_s0 > MINPFR) & (peakfrs_e2_s0 < MAXPFR)

# STATS / DEBUG
pfilt1 = np.sum(ind_m8_1) / float(len(filtind1)) * 100
pfilt2 = np.sum(ind_m8_2) / float(len(filtind2)) * 100
print '%.1f%% E1, %.1f%% E2 (IND_M8)' % (pfilt1, pfilt2)
pfilt1_allr = np.sum(ind_m8_1_allr) / float(len(filtind1)) * 100
pfilt2_allr = np.sum(ind_m8_2_allr) / float(len(filtind2)) * 100
print '%.1f%% E1, %.1f%% E2 (IND_M8_ALLR)' % (pfilt1_allr, pfilt2_allr)

# print m1.shape

# ind = (frs_s2 > frthold) & (frs_s1 > frthold) & (responses > resp_thold) # & (frs_s2 < 15) & (frs_s1 < 15)

#if 'e1' in argv[1]:
#	frs_e2 = np.loadtxt(argv[3].replace('e1', 'e2'))
#	ind = ind & (frs_s1 > 2 * frs_e2)
#else:
#	frs_e1 = np.loadtxt(argv[3].replace('e2', 'e1'))
#	ind = ind & (frs_s1 > 2 * frs_e1)

# ind = (frs_s2 < frthold) & (frs_s1 < frthold) & (np.abs(responses) > resp_thold)

# print ind 
# idx = np.array(range(len(ind)))[ind]
# print type(idx)

#m1 = m1[idix, :]
#m1 = m1[:, idx]
#m2 = m2[:, idx]
#m2 = m2[idx, :]

print 'WARNING: RESPONSE FILTER ONLY ON ONE CELL OUT OF THE COUPLE'

# matrices based only on the cells in the environment
#m1_e1 = m1_e1[ind_m8_1, :]
#m1_e1 = m1_e1[ind_m8_1_allr, :]
#m1_e1 = m1_e1[:, ind_m8_1]
#m2_e1 = m2_e1[ind_m8_1, :]
#m2_e1 = m2_e1[ind_m8_1_allr, :]
#m2_e1 = m2_e1[:, ind_m8_1]

# pre-sleep matrix with e1 cells
#mpres_e1 = mpres[ind_m8_1, :]
#mpres_e1 = mpres[ind_m8_1_allr, :]
#mpres_e1 = mpres[:, ind_m8_1]
#mpres_e2 = mpres[ind_m8_2, :]
#mpres_e2 = mpres[ind_m8_2_allr, :]
#mpres_e2 = mpres[:, ind_m8_2]
# IF NO MATRIX FILTERING
mpres_e1 = mpres
mpres_e2 = mpres

#mpost_e1 = mpost_e1[ind_m8_1, :]
#mpost_e1 = mpost_e1[ind_m8_1_allr, :]
#mpost_e1 = mpost_e1[:, ind_m8_1]
#mpost_e2 = mpost_e2[ind_m8_2, :]
#mpost_e2 = mpost_e2[ind_m8_2_allr, :]
#mpost_e2 = mpost_e2[:, ind_m8_2]

#if FT:
	#fm1_e1 = fm1_e1[ind_m8_1, :]
#	fm1_e1 = fm1_e1[ind_m8_1_allr, :]
#	fm1_e1 = fm1_e1[:, ind_m8_1]
	#fm1_e2 = fm1_e2[ind_m8_2, :]
#	fm1_e2 = fm1_e2[ind_m8_2_allr, :]
#	fm1_e2 = fm1_e2[:, ind_m8_2]

#m1_e2 = m1_e2[ind_m8_2, :]
#m1_e2 = m1_e2[ind_m8_2_allr, :]
#m1_e2 = m1_e2[:, ind_m8_2]
#m2_e2 = m2_e2[ind_m8_2, :]
#m2_e2 = m2_e2[ind_m8_2_allr, :]
#m2_e2 = m2_e2[:, ind_m8_2]

# print m1.shape[0], ' cells'
print m1_e1.shape[0], m1_e1.shape[1], 'cells in E1'
print m1_e2.shape[0], m1_e2.shape[1], 'cells in E2'

#m1 = m1.flatten()
#m2 = m2.flatten()
#ind = ~np.isnan(m2) & ~np.isnan(m1) # & (np.abs(m1) > 0.00001) & (np.abs(m2) > 0.00001)
#m1 = m1[ind]
#m2 = m2[ind]

m1l_e1 = []
m2l_e1 = []
m1l_e2 = []
m2l_e2 = []
lmpres_e1 = []
lmpres_e2 = []
# firt trial lists
lfm1_e1 = []
lfm1_e2 = []
lpost_e1 = []
lpost_e2 = []

# form lists of correlations:
for i in range(m1_e1.shape[0]):
	#for j in range(min(i, m1_e1.shape[1])):
	for j in range(m1_e1.shape[1]):
		#if not np.isnan(m1_e1[i, j]) and not np.isnan(m2_e1[i,j]) and i < j:
		#if True:
		if i < j and ind_m8_1[i] and ind_m8_1_allr[j]:
			m1l_e1.append(m1_e1[i,j])		
			m2l_e1.append(m2_e1[i,j])
			lmpres_e1.append(mpres_e1[i,j])
			if FT:
				lfm1_e1.append(fm1_e1[i,j])
			lpost_e1.append(mpost_e1[i,j])

for i in range(m1_e2.shape[0]):
	#for j in range(min(i, m1_e2.shape[1])):
	for j in range(m1_e2.shape[1]):
		#if not np.isnan(m1_e2[i, j]) and not np.isnan(m2_e2[i,j]) and i < j:
		#if True:
		if i < j and ind_m8_2[i] and ind_m8_2_allr[j]:
			m1l_e2.append(m1_e2[i,j])		
			m2l_e2.append(m2_e2[i,j])
			lmpres_e2.append(mpres_e2[i,j])
			lpost_e2.append(mpost_e2[i,j])
			if FT:
				lfm1_e2.append(fm1_e2[i,j])

#cc = np.corrcoef(m1, m2)[0, 1]

print 'CORLIST LENS: %d / %d' % (len(m1l_e1), len(m1l_e2))

# compute correlation on correlations + write it and raw values of correlations [ e.g. to form a full list in the future ]
if len(m1l_e1) > 0:
	foutcl_e1 = open(FOUTPREF + '.corlist_e1', 'w')
	for i in range(len(m1l_e1)):
		foutcl_e1.write('%f %f %f %f %f\n' % (m1l_e1[i], m2l_e1[i], lmpres_e1[i], lfm1_e1[i] if FT else 0, lpost_e1[i]))
	foutcl_e2 = open(FOUTPREF + '.corlist_e2', 'w')
	for i in range(len(m1l_e2)):
		foutcl_e2.write('%f %f %f %f %f\n' % (m1l_e2[i], m2l_e2[i], lmpres_e2[i], lfm1_e2[i] if FT else 0, lpost_e2[i]))

	cc_e1 = np.ma.corrcoef(m1l_e1, m2l_e1)[0, 1]
	print 'Co-firing correlations in E1: ', cc_e1
	cc_e2 = np.ma.corrcoef(m1l_e2, m2l_e2)[0, 1]
	print 'Co-firing correlations in E2: ', cc_e2

	fout_e1 = open(FOUTPREF + '.cofcorr_e1', 'w')
	fout_e1.write(str(cc_e1) + '\n')
	fout_e2 = open(FOUTPREF + '.cofcorr_e2', 'w')
	fout_e2.write(str(cc_e2) + '\n')
else:
	print 'WARNING: NO CELLS, write empty list / nan correlation files'
	foutcl_e1 = open(FOUTPREF + '.corlist_e1', 'w')
	fout_e1   = open(FOUTPREF + '.cofcorr_e1', 'w')
	foutcl_e2 = open(FOUTPREF + '.corlist_e2', 'w')
	fout_e2   = open(FOUTPREF + '.cofcorr_e2', 'w')

	fout_e1.write('nan\n')
	fout_e2.write('nan\n')
