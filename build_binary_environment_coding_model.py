#!/usr/bin/env python

from scipy.stats import poisson
import os
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from iutils import *
from scipy.stats import ttest_rel, ttest_ind, wilcoxon
from math import sqrt
from tracking_processing import *

if len(argv) < 8:
	print 'USAGE: (1)<base name for clu/res and whl> (2)<speed filter> (3)<max number of spikes> (4)<window size (ms)> (5)<minimal total occurence> (6)<filename> (7)<number of x bins>'
	exit(0)

argv = resolve_vars(argv)

WIN = 24 * int(argv[4])
MAXN = int(argv[3])
SPLIM = float(argv[2])
MINTO = int(argv[5])
FOUTPATH = argv[6]
NBIN = int(argv[7])

# load goal coordinates
goals = [float(f) for f in resolve_vars(['%{g1x}', '%{g1y}', '%{g2x}', '%{g2y}'])]
goals = [[goals[0], goals[1]], [goals[2], goals[3]]]
print 'Goals: ', goals

# testing - 0 load model if exists
VAL = False
if os.path.isfile(FOUTPATH + '.npy'):
	VAL = True
	[dum1, dum2, eptest] = np.load(FOUTPATH + '.npy')
	ncorr = 0
	nnan = 0
	print 'SHAPE OF LOADED MODEL: ', eptest.shape

base = argv[1]
clu = [int(c)-1 for c in open(base + 'clu')]
res = [int(c) for c in open(base + 'res')]
whl = whl_to_pos(open(base + 'whl.scaled'), False)
whllin = whl_to_pos(open('../9l/' + base + 'whl.linear'), False)
speed = whl_to_speed(whl)
NCELL = max(clu) + 1

WMULT = 480
EPS = 0.001

BINMODE = True

# count = nspikes [env, cell, number of spikes]
# NBIN = 86 if BINMODE else 2
# print 'WARNING: NBINS = ', NBIN

nspikes = np.zeros((NBIN, NCELL, MAXN + 1))
envcount = [0] * NBIN
deccount = [0] * NBIN
nstat = []

# calculate probabilities of N spikes ofr every cell
t = -WIN
ires = 0
GOALMODE = False
if GOALMODE:
	print 'WARNING: GOALS ONLY CONSIDERED'
while ires < len(res):	
	nsp = [0] * (NCELL)
	t += WIN

	whli = (t + WIN / 2) / WMULT
	if whli >= len(speed):
		break
	sp = speed[whli]
	# GOAL MODE
	DTHOLD = 20
	if sp < SPLIM or abs(whl[whli][0]) < EPS or GOALMODE and ((distance(whl[whli], goals[0]) > DTHOLD) and (distance(whl[whli], goals[1]) > DTHOLD)):
		continue

	while ires < len(res) and res[ires] < t + WIN:
		nsp[clu[ires]] += 1
		ires += 1

	# assumes bin size is 4
	bin = int(round(whllin[whli][0] / 4.0)) if BINMODE else int(whl[whli][0] > NBIN * 2)
	envcount[bin] += 1
	for c in range(NCELL):
		if nsp[c] > MAXN:
			nspikes[bin][c][MAXN] += 1
		else:
			nspikes[bin][c][nsp[c]] += 1

	if VAL:
		pe1 = 0
		pe2 = 0
		binprobs = [0] * NBIN
		for c in range(NCELL):
			#if (nsp[c]) > 0: # -1.5% accuracy
			binprobs += eptest[:, c, min(nsp[c], MAXN)]

			# before bin mode
			#pe1 += eptest[c, min(nsp[c], MAXN)]
			#pe2 += np.log(1-np.exp(eptest[c, min(nsp[c], MAXN)]))
		# print pe1-pe2
		# print binprobs
		pe1 = np.nanmax(binprobs[:NBIN/2])
		pe2 = np.nanmax(binprobs[NBIN/2:])
		# correct fo binary case as well
		if (pe1 > pe2) == (bin < NBIN/2):
			ncorr += 1
		if np.isnan(pe1) or np.isnan(pe2):
			nnan += 1

		deccount[np.nanargmax(binprobs)] += 1

	nstat.append(sum(nsp))
	
print 'Mean/median spike number: %.2f / %.2f' %(np.mean(nstat), np.median(nstat))

if VAL:	
	print 'Correct: %.2f %%' % (float(ncorr-nnan)/(np.sum(envcount)-nnan) * 100)

print envcount
nspikeprobs = np.zeros((NBIN, NCELL, MAXN + 1))
for b in range(NBIN):
	nspikeprobs[b,:,:] = nspikes[b,:,:] / float(envcount[b])

# CALCULATE POISSON PROBABILITIES
poisslikes = np.zeros((NBIN, NCELL, MAXN + 1))
for b in range(NBIN):
	for c in range(NCELL):
		cbmeanrate = np.sum(nspikes[b,c,:] * np.arange(0,MAXN+1)) / float(np.sum(nspikes[b,c,:]))
		if cbmeanrate < 0.1 or np.isnan(cbmeanrate):
			poisslikes[b,c,0] = 0
			poisslikes[b,c,1:] = -500
		else:
			for n in range(MAXN + 1):
				poisslikes[b,c,n] = poisson.logpmf(n, cbmeanrate)

# eprobs - invalid for the BINMODE
eprobs = nspikeprobs[0,:,:] / (nspikeprobs[0,:,:] + nspikeprobs[1,:,:])
eprobs[ (nspikes[0,:,:] + nspikes[1,:,:]) < MINTO ] = 0.5
eprobs[np.isnan(eprobs)] = 0.5
eprobs[eprobs == 1.0] = 0.5
eprobs[eprobs == 0] = 0.5

np.core.arrayprint._line_width = 220
float_formatter = lambda x: "%.3f" % x
np.set_printoptions(formatter={'float_kind':float_formatter}, threshold=1000000)

nflat = 0
for c in range(NCELL):
	if np.sum(nspikes[:,c,1:]) < MINTO:
		nflat += 1
		nspikeprobs[:,c,:] = np.ones((NBIN, MAXN+1)) / (MAXN+1)
		poisslikes[:,c,:] = np.log(np.ones((NBIN, MAXN+1)) / (MAXN+1))
		# print 'Uniform Cell', c

print '%d cells filtered out' % nflat
# print eprobs
# print nspikeprobs[20,:,:]
# print poisslikes[20,:,:]

np.save(FOUTPATH, (np.log(eprobs), np.log(nspikeprobs), poisslikes))
#np.save(FOUTPATH + '.s', np.log(nspikeprobs))
#np.save(FOUTPATH + '.poiss', poisslikes)

# dump accuracy to the temporary file
if VAL:
	ftmp = open('tmpvalacc', 'w')
	ftmp.write(str(float(ncorr)/(sum(envcount)) * 100) + '\n')

print deccount

# validation
for b in range(NBIN):
        for c in range(NCELL):
		for n in range(MAXN + 1):
			if np.isnan(poisslikes[b,c,n]) or np.isinf(poisslikes[b,c,n]):
				#print "FAIL", b,c,n
				pass
