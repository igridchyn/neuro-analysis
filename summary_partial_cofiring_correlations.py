#!/usr/bin/env python

# collect all residuals of co-firing fits and correlate them

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
import statsmodels.api as sm

if len(argv) < 3:
	print 'USAGE: (1)<residuals file name> (2)<directories list>'
	exit(0)

fres = argv[1]
resids = [[] for i in range(4)]
cdir = os.getcwd()

# non-partial, filtered values
# clistca1/2 clista1/2, clistb1/2
allcorrs = [[] for i in range(6)]

for line in open(argv[2]):

	os.chdir(line[:-1])
	[swap, fresd] = resolve_vars(['%{swap}', fres])
	# load 4 residual lists
	dresid = np.load(fresd)
	os.chdir(cdir)

	if swap:
		for i in range(2):
			resids[i+2].extend(list(dresid[i]))
			resids[i].extend(list(dresid[i+2]))

		for i in range(3):
			allcorrs[2*i].extend(list(dresid[2*i+1 + 4]))
			allcorrs[2*i+1].extend(list(dresid[2*i + 4]))
	else:
		for i in range(4):
			resids[i].extend(list(dresid[i]))

		for i in range(6):
			allcorrs[i].extend(list(dresid[i+4]))

	# also non-partial valuea are written in dresid, load them
for i in range(6):
	allcorrs[i] = np.array(allcorrs[i])

# common lists for partial correlations !
print 'WARNING: residuals overridding by fitting the merged model'
[clistca1, clistca2, clista1, clista2, clistb1, clistb2] = allcorrs

ind1 = ~np.isnan(clista1) & ~np.isnan(clistca1) & ~np.isnan(clistb1)
ind2 = ~np.isnan(clista2) & ~np.isnan(clistca2) & ~np.isnan(clistb2)

lmaa1 = sm.OLS(clista1[ind1], clistca1[ind1], missing='drop')
resaa1 = lmaa1.fit().resid
lmaa2 = sm.OLS(clista2[ind2], clistca2[ind2], missing='drop')
resaa2 = lmaa2.fit().resid
lmba1 = sm.OLS(clistb1[ind1], clistca1[ind1], missing='drop')
resba1 = lmba1.fit().resid
lmba2 = sm.OLS(clistb2[ind2], clistca2[ind2], missing='drop')
resba2 = lmba2.fit().resid

resids = [resaa1, resba1, resaa2, resba2]

for i in range(4):
	print len(resids[i])
	resids[i] = np.array(resids[i])

nindc = ~np.isnan(resids[2]) & ~np.isnan(resids[3])
nindt = ~np.isnan(resids[0]) & ~np.isnan(resids[1])

print 'Control parr corr:', np.corrcoef(resids[2][nindc], resids[3][nindc])[0,1], 'n =', np.sum(nindc)
print 'Target  parr corr:', np.corrcoef(resids[0][nindt], resids[1][nindt])[0,1], 'n =', np.sum(nindt)
