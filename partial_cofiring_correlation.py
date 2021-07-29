#!/usr/bin/env python

from sys import argv
import numpy as np
import statsmodels.api as sm
from iutils import *
from matplotlib import pyplot as plt

# above diagonal with given indices
def above_ind(m, ind):
	c = []
	for i in range(m.shape[0]):
		for j in range(i):
			if ind[i] & ind[j]:
				c.append(m[i,j])

	return np.array(c)

if len(argv) < 5:
	print 'USAGE: (1)<control cofirings> (2)<cofirings to correlate> (3)<pfs file for filtering> (4)<residuals output file>'
	exit(0)

argv = resolve_vars(argv)

pfspath = argv[3]
residpath = argv[4]

# cofiring and cofiring control - before and after
[cofcb, cofca] = np.load(argv[1])
[cofb,   cofa] = np.load(argv[2])

# DEBUG
DEBUG = False
if DEBUG:
	np.fill_diagonal(cofcb, 0)
	np.fill_diagonal(cofb, 0)
	plt.imshow(cofcb-cofb, interpolation = 'none')
	plt.colorbar()
	plt.show()

# assume having filtered indices - SAVE from other methods???
# ind = [True] * corr1.shape[0]
ind1, ind2 = cell_filter('..', pfspath, 0.5, 0.3, '0', 1.5, 0, 5)
# most loose
#ind1, ind2 = cell_filter('..', pfspath, 0.0, 1.0, '0', 1, 0, 100)
print '%.f %% passing' % (np.sum(ind1) / float(len(ind1)) * 100)
print '%.f %% passing' % (np.sum(ind2) / float(len(ind2)) * 100)

print ind1, ind2

clistca1 = above_ind(cofca, ind1)
clistca2 = above_ind(cofca, ind2)
clista1 =  above_ind(cofa, ind1)
clista2 =  above_ind(cofa, ind2)
clistb1 =  above_ind(cofb, ind1)
clistb2 =  above_ind(cofb, ind2)

JOINT = True
if not JOINT:
	# Y, X
	lmaa1 = sm.OLS(clista1, clistca1)
	resaa1 = lmaa1.fit().resid
	lmaa2 = sm.OLS(clista2, clistca2)
	resaa2 = lmaa2.fit().resid
	lmba1 = sm.OLS(clistb1, clistca1)
	resba1 = lmba1.fit().resid
	lmba2 = sm.OLS(clistb2, clistca2)
	resba2 = lmba2.fit().resid
	print 'Normal 1:' , np.corrcoef(clistb1, clista1)[0,1]
	print 'Partial 1:', np.corrcoef(resaa1, resba1)[0,1]
	print 'Normal 2:' , np.corrcoef(clistb2, clista2)[0,1]
	print 'Partial 2:', np.corrcoef(resaa2, resba2)[0,1]

	#np.save(residpath, [resaa1, resba1, resaa2, resba2])
else:
	# JOINT MODEL
	lmaa = sm.OLS(np.concatenate((clista1, clista2)), np.concatenate((clistca1, clistca2)))
	lmba = sm.OLS(np.concatenate((clistb1, clistb2)), np.concatenate((clistca1, clistca2)))
	resaa = lmaa.fit().resid
	resba = lmba.fit().resid
	l1 = len(clista1)
	# DEBUG
	# print clistca1, clistca2, clista1, clista2, clistb1, clistb2
	np.save(residpath, [resaa[:l1], resba[:l1], resaa[l1:], resba[l1:], clistca1, clistca2, clista1, clista2, clistb1, clistb2])
