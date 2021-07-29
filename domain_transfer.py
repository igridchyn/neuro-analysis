#!/usr/bin/env python

import os
from sys import argv
import numpy
from matplotlib import pyplot
from sklearn import manifold
from sklearn.metrics import euclidean_distances
import numpy as np
import random
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from iutils import read_float_list, read_int_list
from sklearn import svm
from sklearn.externals import joblib

if len(argv) < 7:
	print 'Usage: ' + argv[0] + ' (1)<classifier path> (2)<population vectors waking> (3)<population vectors sleep> (4)<waking GT environment> (5)<transferred classifier save path> (6)<sample batch size>'
	exit(0)

# load classifier and test set with labels
clf = joblib.load(argv[1]) 
clf_orig = clf

# iteratively classify sleep vectors + modify training set
popv_w = read_float_list(argv[2])
popv_s = read_float_list(argv[3])

envs = np.array(read_int_list(argv[4]))

# test how different is the classifier and what is it's confidences distribution compared to the original one

# number of transferred samples of each class at each iteration
SAMPLE_BATCH = int(argv[6])
iters = min(sum(envs == 0), sum(envs == 1))

# 0 if original vector, 1 - if transferred
popv_w = np.array(popv_w)
popv_s = np.array(popv_s)
# indices of original vectors in the train array
orig_inds = np.array(range(0, popv_w.shape[0]))
train = popv_w
target = popv_s

print 'Read %d waking vectors, dimension = %d and %d sleep vectors, dimension = %d' % (popv_w.shape[0], popv_w.shape[1], popv_s.shape[0], popv_s.shape[1])

niter = min(popv_w.shape[0], popv_s.shape[0]) / (2*SAMPLE_BATCH)
for i in range(0, niter):
	print 'Iteraton %d out of %d ' % (i, niter)
	# predict with current classifier and find indices of the least confident original points in each of the environments
	trprobs = clf.predict_proba(train)
	clsf = trprobs[:, 0] < trprobs[:, 1]
	# nex one this gives same points for both environments
 	#sind = np.concatenate([np.argsort(trprobs[orig_inds][0])[0:SAMPLE_BATCH], np.argsort(trprobs[orig_inds][1])[0:SAMPLE_BATCH]])
	trord = np.argsort(np.max(trprobs[orig_inds,:], 1))
	sind1 = []
	sind2 = []
	i = 0
	stop = False
	while len(sind1) < SAMPLE_BATCH or len(sind2) < SAMPLE_BATCH:
		if i >= len(trord):
			stop = True
			break

		if clsf[orig_inds[trord[i]]] == 0:
			if len(sind1) < SAMPLE_BATCH:
				sind1.append(trord[i])
		else:
			if len(sind2) < SAMPLE_BATCH:
				sind2.append(trord[i])
		i += 1
	sind = np.array(sind1 + sind2)

	if stop:
		print 'Emergency exit'
		break

	# remove from original indices
	del_list =  np.sort(sind)[::-1]
	for ind in del_list:
		orig_inds = np.delete(orig_inds, ind, None)
	
	# find the most confident target domain points
	targprobs = clf.predict_proba(target)
	# most confident samples cannot have high confidence for both classes
	tind = np.concatenate([np.argsort(targprobs[:,0])[targprobs.shape[0] - SAMPLE_BATCH : ], np.argsort(targprobs[:,1])[targprobs.shape[0] - SAMPLE_BATCH : ]])
	
	# substitute the least probable from waking from the most probable from sleep and remove them from sleep
	# ? same size ?
	for s in range(0, 2 * SAMPLE_BATCH):
		print s, sind[s], tind[s]
		train[sind[s]] = target[tind[s]]
	del_tar = np.sort(tind)[::-1]
	for s in del_tar:
		target = np.delete(target, s, 0)

	# retrain the classifier for the new training set
	print 'Start classifier training'
	clf = svm.SVC(kernel='rbf', probability = True)
        clf.fit(train, envs)

joblib.dump(clf, argv[5])
