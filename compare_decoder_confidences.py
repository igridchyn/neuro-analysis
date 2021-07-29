#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
from numpy import abs, log
import os

if len(argv) < 4:
	print 'Usage: ' + argv[0] + ' (1)<confidences 1> (2)<confidences 2> (3)<[ll | pp | pl | lp] - logs or probs for each classifier; s-SVM format, 2 columns with ps for each class>'
	exit(0)

def percentile_similar(cfs1, cfs2, percentile, baseline):
	cfs1 = np.array(cfs1)
	cfs2 = np.array(cfs2)

	if baseline:
		cfs1 -= np.mean(cfs1)
		cfs2 -= np.mean(cfs2)

	p1 = np.percentile(abs(cfs1), percentile)
	#print p1
	
	ind = abs(cfs1) > p1

	#print ind
	return sum((cfs1[ind] > 0) == (cfs2[ind] > 0)) / float(sum(ind))

if argv[3][0] == 's':
	confs1 = []
	for l in open(argv[1]):
		c = l.split(' ')
		if len(c) < 2:
			continue
		confs1.append(log(float(c[0]) - log(float(c[1]))))
else:
	confs1 = [float(c) for c in open(argv[1]) if len(c) > 0]
if argv[3][1] == 's':
	confs2 = []
	for l in open(argv[2]):
		c = l.split(' ')
		if len(c) < 2:
			continue
		confs2.append(log(float(c[0]) - log(float(c[1]))))
else:
	confs2 = [float(c) for c in open(argv[2]) if len(c) > 0]

if len(confs1) != len(confs2):
	print 'DIfferent number of decodings: %d / %d' % (len(confs1), len(confs2))
	exit(1)

confs1 = np.array(confs1)
confs2 = np.array(confs2)
flen = float(len(confs1))

if argv[3][0] == 'p':
	confs1 = log(confs1)
if argv[3][1] == 'p':
	confs2 = log(confs2)

print 'Mean confidences: %r / %f' % (np.mean(confs1), np.mean(confs2))

print 'Number of predictions per class, classifier 1: %d / %d' % (sum(confs1 > 0), sum(confs1 < 0))
print 'Number of predictions per class, classifier 2: %d / %d' % (sum(confs2 > 0), sum(confs2 < 0))

print 'Same ennvironment predicted: %.2f' % (sum((confs1 > 0) == (confs2 > 0)) / flen)
print 'Same ennvironment predicted with baseline consideration : %.2f' % (sum((confs1 > np.mean(confs1)) == (confs2 > np.mean(confs2))) / flen)

perc = range(0, 99)

cons1 = []
cons2 = []
for p in perc:
	cons1.append(percentile_similar(confs1, confs2, p, True))
	cons2.append(percentile_similar(confs2, confs1, p, True))

plt.plot(perc,cons1)
plt.plot(perc,cons2, color='r')
plt.grid()
plt.xlabel('Decoder confidence percentile')
plt.ylabel('% of aggreed classifications')
plt.legend([argv[1], argv[2]], loc=0)
plt.show()
