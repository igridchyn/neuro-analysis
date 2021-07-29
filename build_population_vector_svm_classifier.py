#!/usr/bin/env python

from sklearn import svm
from sklearn.externals import joblib
from iutils import *
import random
from sys import argv
import numpy as np

if len(argv) < 4:
	print 'Usage: ' + argv[0] + '(1)<1st class vectors> (2)<2nd class vectors> (3)<classifier path>'
	print 'Build and save population vector classifier, report 70/30 CV precisoin. Duplicates population_vector_classifier?'
	exit(0)

popvs1 = read_float_array(argv[1])
popvs2 = read_float_array(argv[2])

print 'Loaded %d vectors of class 1 and %d vectors of class 2' % (popvs1.shape[0], popvs2.shape[0])

popvecs = np.concatenate((popvs1, popvs2))
classes = np.array([0] * popvs1.shape[0] + [1] * popvs2.shape[0])

# TODO: cv 70 / 30 before main fit
itrain = random.sample(range(0, classes.shape[0]), classes.shape[0] * 70/100)
itest = [i for i in range(0, classes.shape[0]) if i not in itrain]

clf_cv = svm.SVC(kernel='rbf', probability = False)
clf_cv.fit(popvecs[itrain,:], classes[itrain])

clsf_test = clf_cv.predict(popvecs[itest,:])
print 'CV (70/30) accuracy: %.2f' % (sum(classes[itest] == clsf_test) / float(len(itest)))

# select train and test sets for the CV run


clf = svm.SVC(kernel='rbf', probability = True)
clf.fit(popvecs, classes)

joblib.dump(clf, argv[3])
