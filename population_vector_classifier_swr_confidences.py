#!/usr/bin/env python

from sys import argv
from sklearn import svm
from sklearn.externals import joblib
import numpy as np
from numpy import log
from statsmodels.distributions.empirical_distribution import ECDF
from matplotlib import pyplot as plt

if len(argv) < 10:
	print 'Usage: ' + argv[0] + ' (1)<path to dir with all.*> (2)<swr file> (3)<spike number> (4)<window around> (5)<model path> (6)<CMAP (which cells to use) file> (7)<output file / directory> (8)<spike overlap> (9)<norm file or ->'
	exit(0)

res = [int(r) for r in open(argv[1] + 'all.res') if len(r) > 0]
clu = [int(c) for c in open(argv[1] + 'all.clu') if len(c) > 0]

swrs = [int(s) for s in open(argv[2]) if len(s) > 0]


SN = int(argv[3])
SOVER = int(argv[8])
WIN = int(argv[4])

ires = 0

cmap = [int(c) for c in open(argv[6]) if len(c) > 0]
cused = len(cmap) - cmap.count(-1)
print 'Number of cells used : %d' % cused
print 'Cmap: ' + str(cmap)
# exit(0)

if argv[7].endswith('/'):
	DIRDUMP = True
	fconf = open(argv[7] + 'confidences.txt', 'w')
	fclsf = open(argv[7] + 'clsf.txt', 'w')
else:
	DIRDUMP = False
	fout = open(argv[7], 'w')

clf = joblib.load(argv[5])

means = []
stds = []
NORM = False
if argv[9] != '-':
	for line in open(argv[9]):
		if len(line.split(' ')) > 1:
			means.append(float(line.split(' ')[0]))
			stds.append(float(line.split(' ')[1]))
	NORM = True
	means = np.array(means)
	stds = np.array(stds)
	print 'Loaded means / stds for normalization'

popvecs = []
envocc = [0, 0]
confidences = []
for swi in range(0, len(swrs)):
	swr = swrs[swi]

	while res[ires] < swr - WIN:
		ires += 1

	# if going to skip
	if res[ires] >= swr + WIN and DIRDUMP:
		fconf.write('0\n')
		fclsf.write('0\n')
		popvecs.append(np.zeros((cused, 1)))
		print 'SKIP'

	while res[ires] < swr + WIN:

		popvec = np.zeros((cused, 1))
		spikes_counted = 0
		#for i in range(ires, min(ires + SN, len(res))):
		i = ires
		while i < len(res) and spikes_counted < SN:
			if cmap[clu[i]] >= 0:
				popvec[cmap[clu[i]]] += 1
				spikes_counted += 1
			i += 1

		if NORM:
			#print popvec, means
			#print popvec.shape, means.shape
			popvec[:,0] -= means
			popvec[:,0] /= stds

		# print popvec.transpose()
		# print popvec.shape

	    	# p = clf.predict_proba(popvec.transpose())[0]
	    	p = clf.decision_function(popvec.transpose())[0]
	    	e = clf.predict(popvec.transpose())[0]
		envocc[e] += 1
		# print e
		# print p
	
		popvecs.append(popvec)

		if i >= len(res):
			break
	
		confidences.append(abs(p[0]))

		if DIRDUMP:	
			fconf.write(str((log(p[0]) - log(p[1]))) + '\n')
			# fclsf.write(str(p[0] > p[1]) + '\n')
			# only one prediction per SWR
			break
		else:
			mult = 1.0 if e == 0 else -1.0
			fout.write('%d %d %f %f %f %f\n' % (swi, (res[ires] + res[i]) / 2, p*mult, -p*mult, p, p))	
			# fout.write('%d %d %f %f %f %f\n' % (swi, (res[ires] + res[i]) / 2, log(p[0]), log(p[1]), p[0], p[1]))	
		
		ires = i

print 'Envocc:', envocc

# dump population vectors
if DIRDUMP:
	print 'Writing population vectors'
	fpop = open(argv[7] + 'swr_' + argv[3] + '_' + argv[4] + '.popvec', 'w')
	for pop in popvecs:
		for p in pop:
			fpop.write('%f ' % p)
		fpop.write('\n')
	fpop.close()
	

if DIRDUMP:
	fconf.close()
	fclsf.close()
else:
	fout.close()

# PLOT CONFIDENCES ECDF
# print confidences
ecdf = ECDF(confidences)
x = np.linspace(min(confidences), max(confidences), num=400)
y = ecdf(x)
plt.figure()
plt.plot(y, x)
plt.grid()
plt.show()

