#!/usr/bin/env python
import numpy as np
import scipy
import os
from sys import argv
import matplotlib.pylab as plt
from scipy import linalg
from scipy import spatial

if len(argv) < 3:
	print 'Show matrix of Kullback-Leibler divergences between clusters (and fitted Gaussians)'
	print "Arguments: (1)<base_path> (2)<tetrode_number>"
	exit()

path = argv[1]
tetr = argv[2]

f = open(path + '.fet.' + tetr)
nfet = int(f.readline())
x = scipy.fromfile(f, sep=' ')
x = x.reshape(x.shape[0] / nfet, nfet)

i = scipy.array(range(0, nfet-5))
x = x[:, i]

fclu = open(path + '.clu.' + tetr)
clu = fclu.read().split('\n')[1:]
clu = [int(c) for c in clu if len(c) > 0]
clun = max(clu)

means = []
covs = []
covis = []
dets = []

for c in range(2, clun + 1):
	# print c

	indc = scipy.array([i for i in range(0, len(clu)) if clu[i] == c])

	print indc.shape

	fetc = x[indc, :]
	
	cov = np.cov(scipy.transpose(fetc))
	covi = linalg.inv(cov)
	mean = scipy.mean(fetc, 0)
	# print mean
	det = np.linalg.det(cov)

	means.append(mean)
	covs.append(cov)
	covis.append(covi)
	dets.append(det)

# compute Kullback-Leibler divergences
dkls = scipy.zeros((clun-1, clun-1))
for c1 in range(0, clun - 1):
	for c2 in range(0, clun - 1):
		# print c1, c2
		md = means[c2] - means[c1]
		dkl = 0.5 * (np.trace(np.dot(covis[c2], covs[c1])) + covis[c2].dot(md).dot(md) - 12 - np.log(dets[c1] / dets[c2]))
		# dkl = covis[c2].dot(md).dot(md)
		dkls[c2, c1] = dkl


# print
for c in range(0, clun-1):
	print 'Closest to ', c+2, ' : ', np.argsort(dkls[c,:]) + 2

if len(argv) == 3:
	plt.imshow(dkls, interpolation = 'nearest')
	plt.colorbar()
	plt.show()
