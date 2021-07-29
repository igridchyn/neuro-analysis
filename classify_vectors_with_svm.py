#!/usr/bin/env python

from iutils import write_array, read_float_array
from sklearn.externals import joblib
from sys import argv
import numpy as np

if len(argv) < 4:
	print 'Usage: ' + argv[0] + ' (1)<classifier path> (2)<vectors path> (3)<output base>'
	exit(0)

clf = joblib.load(argv[1])
vectors = read_float_array(argv[2])

print vectors
probs = clf.predict_proba(vectors)
classes = clf.predict(vectors)

write_array(probs, argv[3] + '.svm_probs')
write_array(classes, argv[3] + '.svm_classes')
