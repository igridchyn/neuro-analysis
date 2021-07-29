#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
from datetime import date
import os
from iutils import *

def npexp(a):
	return np.exp(a)

def zscore(a, msd):
	m = msd[0]
	sd = msd[1]
	l = []
	for e in a:
		l.append((e-m)/sd)
	return np.array(l)

def perc(a):
	return float(sum(a)) / len(a) * 100

def finmean(a):
	return np.nanmean(a[~np.isnan(a) & ~np.isinf(a)])

if len(argv) < 3:
	print 'USAGE: (1)<dump file> (2)<output file> (3)<threshold 1> (4)<threshold 2>'
	print 'OUTPUT: *.redyn file'
	exit(0)

NORM = True
if NORM:
	print 'WARNIING: LIKELIHOODS NORMALIZED!'

# threshold : p20
SWAP = int(resolve_vars(['%{swap}'])[0])
print 'SWAP:', SWAP
d = []
for line in open(argv[1]):
	ws = line.split(' ')
	# likelihood of targ)
	#d.append(float(ws[3 + SWAP])-float(ws[-1]))
	# likelihood of con
	d.append(float(ws[4 - SWAP])-float(ws[-1]))
	# confidence : target - control
	#d.append(float(ws[3 + SWAP])-float(ws[4-SWAP]))
d = np.array(d)
# threshold
d = d[~np.isnan(d) & ~np.isinf(d) & (np.abs(d) > 0.000001) ]
PTHOLD = -np.inf #np.percentile(d, 75)
print 'WARNING: THRESHOLD FOR LIKELIHOOD = %.2f' % PTHOLD

lk1 = []
lk2 = []

# first / last in swr
lkf1 = []
lkf2 = []
lkl1 = []
lkl2 = []
lkaf = []
lkal = []

curswr = -1
EPS = 0.001

# SWR window index
swrwi = 0

# if using number of spikes = N50, then windows to compare are 2 and 5 (0-based)
# if number of spikes = N100, then windows to compare are 0 and 2 (0-based)

# whether passes threshold or not
PASS = False
for line in open(argv[1]):
	ws = line.split(' ')

	swri = int(ws[0])

	if swri > curswr:
		# to have equal size of first and last
		#if swri < 2:
		#	del lkf1[-1]
		#	del lkf2[-1]

		# make sure sizes are equal
		if swrwi < 1:
			lkf1 = lkf1[:-1]
			lkf2 = lkf2[:-1]
			lkal = lkal[:-1]

		swrwi = 0
		#lkl1.append(l1)
		#lkl2.append(l2)			
	else:
		swrwi += 1
		
	l1 = float(ws[3])
	l2 = float(ws[4])
	s1 = float(ws[5])
	s2 = float(ws[6])

	sm = float(ws[11])
	if NORM:
		l1 -= sm # s1 + np.log(50)# -=
		l2 -= sm # s2 + np.log(50)# -=
	ls = [l1, l2]

	if swri > curswr:
		#lkf1.append(l1)
		#lkf2.append(l2)
		curswr = swri
	
	lk1.append(l1)
	lk2.append(l2)

	# if last window == 3rd window (right after the pulse with th 50% overlap)
	if swrwi == 1:
		if PASS:
			lkl1.append(l1)
			lkl2.append(l2)
			lkal.append(sm)

	# 2 for N100 / 3 for N50 windows, both with 50% overlap
	if swrwi == 0:
		# likelihood of target environment
		#PASS = ls[SWAP] > PTHOLD
		# likelihood of control environment
		PASS = True# ls[SWAP] > PTHOLD
		# likelihood of control environment
		# confidence : traget - control
		# PASS = True #(ls[SWAP] - ls[1-SWAP]) > PTHOLD
		if PASS:
			lkf1.append(l1)
			lkf2.append(l2)
			lkaf.append(sm)

lk1 = np.array(lk1)
lk2 = np.array(lk2)
lkf1 = np.array(lkf1)
lkf2 = np.array(lkf2)
lkl1 = np.array(lkl1)
lkl2 = np.array(lkl2)
lkaf = np.array(lkaf)
lkal = np.array(lkal)

print len(lk1), len(lkf1), len(lkl1)

morel1l2 =  (np.nansum(lk1 > lk2)   / float(np.sum(~np.isnan(lk1)  & ~np.isnan(lk2)))  * 100)
morel1l2f = (np.nansum(lkf1 > lkf2) / float(np.sum(~np.isnan(lkf1) & ~np.isnan(lkf2))) * 100)
morel1l2l = (np.nansum(lkl1 > lkl2) / float(np.sum(~np.isnan(lkl1) & ~np.isnan(lkl2))) * 100)
morel2l1 =  (np.nansum(lk2 > lk1)   / float(np.sum(~np.isnan(lk2)  & ~np.isnan(lk1)))  * 100)
morel2l1f = (np.nansum(lkf2 > lkf1) / float(np.sum(~np.isnan(lkf2) & ~np.isnan(lkf1))) * 100)
morel2l1l = (np.nansum(lkl2 > lkl1) / float(np.sum(~np.isnan(lkl2) & ~np.isnan(lkl1))) * 100)

print 'Total L1 > L2, L2 > L1: %.2f %.2f %%' % (morel1l2, morel2l1)
print 'First L1 > L2, L2 > L1: %.2f %.2f %%' % (morel1l2f, morel2l1f)
print 'Last  L1 > L2, L2 > L1: %.2f %.2f %%\n' % (morel1l2l, morel2l1l)

print 'Total mean conf: %.2f' % finmean(lk1 - lk2)
print 'First mean conf: %.2f' % finmean(lkf1 - lkf2)
print 'Last  mean conf: %.2f\n' % finmean(lkl1 - lkl2) 

lkf_ninf = ~np.isinf(lkf1) & ~np.isinf(lkf2)
lkl_ninf = ~np.isinf(lkl1) & ~np.isinf(lkl2)
print 'Total l1 / l2: %.2f / %.2f' %( finmean(lk1), finmean(lk2) )
print 'First l1 / l2: %.2f / %.2f' %( finmean(lkf1[lkf_ninf]), finmean(lkf2[lkf_ninf]) )
print 'Last  l1 / l2: %.2f / %.2f\n' %( finmean(lkl1[lkl_ninf]), finmean(lkl2[lkl_ninf]) )

# correlation coefficients: before and after
ind1 = ~np.isnan(lkf1) & ~np.isnan(lkl1)
ind2 = ~np.isnan(lkf2) & ~np.isnan(lkl2)
corr1 = np.corrcoef(lkf1[ind1], lkl1[ind1])[0,1]
corr2 = np.corrcoef(lkf2[ind2], lkl2[ind2])[0,1]
print 'Correlations of likelihoods before and after, E1 / E2: %.2f / %.2f' % (corr1, corr2)

# PSOPT
ZSCORE = False
if ZSCORE:
	# read mean/sd : L1, L2, SUM, DIFF
	# use norm / not norm versions
	fmsd = open('BOTH_WS_NORM.msd')
	msds = []
	for i in range(4):
		msds.append([float(f) for f in fmsd.readline().split(' ')])

	lkf1 = zscore(lkf1, msds[0])
	lkl1 = zscore(lkl1, msds[0])
	lkf2 = zscore(lkf2, msds[1])
	lkl2 = zscore(lkl2, msds[1])
	lkfd = zscore(lkf1-lkf2, msds[3])
	lkld = zscore(lkl1-lkl2, msds[3])
	lk1 = zscore(lk1, msds[1])
	lk2 = zscore(lk2, msds[1])
else:
	lkfd = lkf1 - lkf2
	lkld = lkl1 - lkl2
	lkd =  lk1  - lk2
	

# fout = open(argv[1] + '.redyn', 'w')
fout = open(argv[2], 'w')
fout.write('%f %f\n' % (morel1l2, morel2l1))
fout.write('%f %f\n' % (morel1l2f, morel2l1f))
fout.write('%f %f\n' % (morel1l2l, morel2l1l))
fout.write(str(finmean(lkd)) + '\n')
fout.write(str(finmean(lkfd)) + '\n')
fout.write(str(finmean(lkld)) + '\n')
fout.write('%e %e\n' % ( finmean(lk1), finmean(lk2) ))
fout.write('%e %e\n' % ( finmean(npexp(lkf1[lkf_ninf])), finmean(npexp(lkf2[lkf_ninf])) ))
fout.write('%e %e\n' % ( finmean(npexp(lkl1[lkl_ninf])), finmean(npexp(lkl2[lkl_ninf])) ))
fout.write('%f %f\n' % (corr1, corr2))

if len(argv) > 3:
	CONF = False
	
	thold1 = float(argv[3])
	if len(argv) > 4:
		thold2 = float(argv[4])
		print 'LIKELIHOOD THRESHOLD MODE'
	else:
		CONF = True
		print 'CONFIDENCE THRESHOLD MODE'

	if not CONF:
		# likelihood thresholds
		tholds1 = np.arange(0, thold1, thold1 / 10)
		tholds2 = np.arange(0, thold2, thold2 / 10)

		p1b = np.array([perc(lkf1 > th1) for th1 in tholds1])
		p1a = np.array([perc(lkl1 > th1) for th1 in tholds1])
		p2b = np.array([perc(lkf2 > th2) for th2 in tholds2])
		p2a = np.array([perc(lkl2 > th2) for th2 in tholds2])
		# ignore for multiple bars
		pob = np.array([perc((lkf1 > tholds1[i]) & (lkf2 > tholds2[i])) for i in range(len(tholds1))])
		poa = np.array([perc((lkl1 > tholds1[i]) & (lkl2 > tholds2[i])) for i in range(len(tholds1))])
	else:
		# confidence thresholds, all use 1 threshold
		tholds = np.arange(0,thold1, thold1 / 10)
		# were: differences, lkf1-lkf2 etc + > thold everywhere
		p1b = np.array([perc(lkf > thold) for thold in tholds])
		p1a = np.array([perc(lkl > thold) for thold in tholds])
		p2b = np.array([perc(lkf < - thold) for thold in tholds])
		p2a = np.array([perc(lkl < - thold) for thold in tholds])
		pob = poa = [0] * len(tholds)
	
	#print '%% of events LIK1 > THOLD1: before / after: %.2f %% / %.2f %%' % (p1b, p1a)
	#print '%% of events LIK2 > THOLD2: before / after: %.2f %% / %.2f %%' % (p2b, p2a)
	#print '%% of events BOTH HIGH    : before / after: %.2f %% / %.2f %%' % (pob, poa)

	pub = 100 - p1b - p2b + pob
	pua = 100 - p1a - p2a + poa

	ind = np.concatenate((np.arange(10), np.arange(13,23)))

	w = 0.3
	a = 0.8

	print p1b, p1a

	PLOT = False

	if PLOT:
		p1 = plt.bar(ind, np.concatenate((p1b, p1a)), width = w, alpha = a)
		p2 = plt.bar(ind, np.concatenate((p2b, p2a)), bottom = np.concatenate((p1b - pob, p1a - poa)), color = 'red', width = w, alpha = a)
		p3 = plt.bar(ind, np.concatenate((pub, pua)), bottom = np.concatenate((p1b + p2b - pob, p1a + p2a - poa)), color = 'grey', width = w)
		plt.xticks((0+ w/2,1 + w/2), ('BEFORE', 'AFTER'))
		plt.legend((p1[0], p2[0], p3[0]), ('ENV1', 'ENV2', 'NONE'), loc = 'best')

		for i in range(len(ind) / 2):
			plt.text(ind[i] + 0.05, 50, '%f' % (p1b[i]/p2b[i]), rotation = 'vertical', fontsize=15)
		for i in range(len(ind) / 2):
			plt.text(ind[i+ len(ind)/2] + 0.05, 50, '%f' % (p1a[i]/p2a[i]), rotation = 'vertical', fontsize=15)

		subtit = os.getcwd().split('/')[-3] + ' - ' + os.getcwd().split('/')[-2] + ' - ' + ('NINH' if 'NINH' in argv[1] else 'INH')

		plt.title(subtit + ('\nLIKELIHOOD thresholds: %f / %f' % (thold1, thold2) if not CONF else '\nCONF threshold: %s' % (thold1)))
		plt.gca().set_ylim([0, 100])

		fpath = '/home/igor/Dropbox/IST_Austria/Csicsvari/Results/' + date.today().strftime('%y-%m-%d') + '/' + argv[1] + '.png'
		plt.savefig(fpath)

		plt.show()
	
	fout.write(('%f '*20 + '\n') % tuple(list(p1b) + list(p1a)))
	fout.write(('%f '*20 + '\n') % tuple(list(p2b) + list(p2a)))

print 'LKAF: ', finmean(np.exp(lkaf))
fout.write('%e %e\n' % (finmean(npexp(lkaf)), finmean(npexp(lkal))))

fout.close()
