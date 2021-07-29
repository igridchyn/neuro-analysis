#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
#import statsmodels as sm
from statsmodels.distributions.empirical_distribution import ECDF
import os.path
from math import sqrt

if len(argv) < 3:
	print argv[0] + '(1)<daylab> (2)<path to directory with bayesian decoder of the learning session output (clsf, errors, confidences)>'
	print 'Plot confidence ECDF / error from confidence'
	print 'Provide multiple direcotries after 2nd argument to plot multiple performance curves'
	exit(0)

def plot_prec_from_conf(base, col):
	if os.path.isdir(base):
		confidences = [float(f) for f in open(base + 'confidences.txt') if len(f) > 0]
		clsfs = [int(i) for i in open(base + 'clsf.txt') if len(i) > 0]
		errors = [float(f) for f in open(base + 'errors.txt') if len(f) > 0]
		likespath = base + 'mlikes1.txt'
		if os.path.isfile(likespath):
			mlikes1 = [float(f) for f in open(likespath) if len(f) > 0]
		else:
			print 'WARNING: no likeslihoods found, fill with 0s'
			mlikes1 = [0] * len(errors)
	else: # read from dump
		f = open(base)
		confidences = []
		clsfs = []
		errors = []
		mlikes1 = []
		print 'WARNING: NO MLIKES'
		for line in f:
			if len(line) < 10:
				continue
			w = [float(f) for f in line.split(' ')]
			confidences.append(abs(w[4]))
			BORD = 172
			clsfs.append([0 if (w[0]-BORD)*(w[2]-BORD) < 0 else 1])
			dist = sqrt((w[0]-w[2])**2 + (w[1]-w[3])**2)
			errors.append(dist)
			mlikes1.append(0)

	print 'Read %d entries of errors/confidences and %d entries of clsfs' % (len(errors), len(clsfs))

	confidences = np.array(confidences)
	clsfs = np.array(clsfs)
	errors = np.array(errors)
	mlikes1 = np.array(mlikes1)

	# valid [above speed limit]
	clsfsv = clsfs[clsfs >= 0]

	print 'Correlation of max likelihood in 1 and confidence: %.2f' % np.corrcoef(mlikes1, confidences)[0, 1]

	# ROC
	csort = np.argsort(confidences) [::-1]

	step = len(confidences) / 30

	pconfs = []
	pprecs = []
	plikes = []

	i = step
	while i < len(confidences):
		#pconfs.append(confidences[csort[i]])
		pconfs.append(i / float(len(confidences)))
		subclsf = clsfsv[csort[i-step:i]]
		pprecs.append(sum(subclsf == 1) / float(step))
		plikes.append(np.mean(mlikes1[csort[i-step:i]]))
		i += step

	fig = plt.figure(2)
	ax = fig.add_subplot(111)
	plt.plot(pconfs, pprecs, lw=5, c=col)
	plt.grid()
	axl = ax.twinx()
	axl.plot(pconfs, plikes, lw=3, c='k')

	return confidences, csort, clsfs

#=========================================================================================================================
daylab=argv[1]

cols = ['b', 'r']
i = 0
legend = [daylab + ': 2nd half on post confidences', daylab + ': 2nd half on 1st half confidences']
for base in argv[2:]:
	confidences, csort, clsfs = plot_prec_from_conf(base, cols[i])
	i += 1

	# plot cumulative
	#ecdf = sm.distributions.ecdf(confidences)
	ecdf = ECDF(confidences)
	x = np.linspace(min(confidences), max(confidences), num=400)
	y = ecdf(x)

	plt.figure(1)
	plt.step(y, x, c=cols[i-1])
	# plt.show()

	#plt.hist(confidences, 100)
	#plt.show()

	clsfs = np.array(clsfs)
	prec = (sum(clsfs > 0) / float(sum(clsfs >= 0)))

	print 'Overall precision : %.3f' % prec
	legend[i - 1] += ', acc. = %.3f' % prec


plt.figure(1)
plt.ylabel('confidence')
plt.xlabel('quantile')
plt.title('Confidences ECDF')
plt.grid()
plt.legend(legend, loc=0)
plt.gca().invert_xaxis()
# plt.show()

plt.figure(2)
plt.title('AUC = classification accuracy')
plt.xlabel('1 - confidence percentile')
plt.ylabel('Classification accuracy')
plt.grid()
plt.legend(legend, loc=3)
# plt.gca().invert_xaxis()
plt.show()
