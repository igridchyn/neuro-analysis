#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
import os
from statsmodels.distributions.empirical_distribution import ECDF
from numpy import abs

# ======================================================================================================================
def load_ints(path):
	return [int(r) for r in open(path) if len(r) > 0]
# ======================================================================================================================

def read_preds(nameformat):
	swri=0
	preds = []
	path = nameformat % swri
	while os.path.isfile(path):
		pred = np.genfromtxt(path)

		preds.append(pred)

		swri += 1
		path = nameformat % swri
	print 'Loaded %d SWRs' % (len(preds))
	return preds
# ======================================================================================================================

def dump_stats(preds):
	andir = os.path.dirname(argv[1]) + '/analyses/'
	if not os.path.isdir(andir):
		os.mkdir(andir)

	print 'Loaded %d matrices' % len(preds)

	nbx = preds[0].shape[1]
	nby = preds[0].shape[0]

	print 'Dump stats to ' + andir + 'confidences.txt'

	fconfs = open(andir + 'confidences.txt', 'w')
	for pred in preds:
		confidence = np.max(pred[0:nby/2,:]) - np.max(pred[nby/2:,:])
		fconfs.write('%f\n' % confidence)
# ======================================================================================================================
def plot_ecdf(confidences, ci):
	ecdf = ECDF(confidences)
	x = np.linspace(min(confidences), max(confidences), num=400)
	y = ecdf(x)

	cols = ['b', 'r']
	plt.figure(1)
	plt.step(y, x, c=cols[ci])
# ======================================================================================================================
def env_and_confidence(pred, envb, bias):
	mx1 = np.max(pred[0:envb, :])
	mx2 = np.max(pred[envb:, :]) 
	env = (mx1 -mx2 + bias) * max(mx1,mx2)
	return int(env > 0), np.abs(env)
# ======================================================================================================================


if len(argv) < 3:
        print 'Usage: ' + argv[0] + '(1)<dumped matrices prefix> (2 optional)<file with all SWR timestamps> (3 optional)<file with part of SWRs / directory with additional dump>'
        print 'Analyze dumped by LFPO swr prediction matrices'
	exit(0)

# analyze subset of SWRs
preds = read_preds(argv[1] + 'swr_%d_0_0.mat')
swrs = load_ints(argv[2])
smat = np.zeros(preds[0].shape)

if len(argv) > 3 and not os.path.isfile(argv[3]):
	print 'Compare two sets of decodings...'
	preds2 = read_preds(argv[3])
 	print 'Loaded %d alternative predictions ' % len(preds2)

	nby = preds[0].shape[0]
	same = 0
	confs1 = []
	confs2 = []
	es1 = []
 	es2 = []
	sconfs1 = []
	sconfs2 = []
	for pi in range(0, len(preds)):
		e1, c1 = env_and_confidence(preds[pi], 50, 140)
		e2, c2 = env_and_confidence(preds2[pi], 50, 13)
		confs1.append(c1)
		confs2.append(c2)
		es1.append(e1)
		es2.append(e2)
		sconfs1.append(c1 if e1 == 0 else -c1 )
		sconfs2.append(c2 if e2 == 0 else -c2 )
		if e1 == e2:
			same += 1
	plt.hist(sconfs1, 30)
	plt.hist(sconfs2, 30, color='r')
	plt.legend(['Confidences WS-based', 'Confidences Bayesian'])
	plt.show()

	confs1 = np.array(confs1)
	confs2 = np.array(confs2)
	print 'Same predictions : %.2f' % (same / float(len(preds)))
	print '1st environment prediction rate by alternative / main: %.2f / %.2f' % (sum(es2)/float(len(es2)), sum(es1)/float(len(es1)))
	q = 90
	percentile = np.percentile(abs(confs1), q)
	subes1 = np.array(es1)[abs(confs1) > percentile]
	subes2 = np.array(es2)[abs(confs1) > percentile]
	print 'Same predictions with %d percent of most confident (acc. to main prediction confidence) events: %.2f' % (100-q, sum(subes1 == subes2) /(float(len(subes1))))
	print 'Confidences correlation: %.2f' % np.corrcoef(sconfs1, sconfs2)[0, 1]

# analyze non-inhibited SWRs
if len(argv) > 3 and os.path.isfile(argv[3]):
	swrs_ninh = load_ints(argv[3])
	predleft = 0
	for swni in swrs_ninh:
		pred = preds[swrs.index(swni)]	
		envb = pred.shape[0]/2
		smat += pred
		if np.max(pred[0:envb,:]) > np.max(pred[envb:,:]) - 150:
			predleft += 1
	print 'Summed up %d swrs' % len(swrs_ninh)
	print 'Fraction of predicted left environment: %.2f' % (predleft / float(len(swrs_ninh)))
	plt.imshow(smat)
	plt.show()
else:
	print 'To analyze part of swrs, provide 3rd parameter'

# dump starts of most confident events in each of the environments
CTHOLD = 30000 # 30000 for WS-based; 2000 for Bayesian
fswrs1 = open('swrs1.txt', 'w')
fswrs2 = open('swrs2.txt', 'w')
fswrs = [fswrs1, fswrs2]
cswrs = [0, 0]
print preds[0].shape
for si in range(0, len(swrs)):
	env, conf = env_and_confidence(preds[si], 50, 140) # 18 for Bayesian
	if conf > CTHOLD:
		fswrs[env].write(str(swrs[si]) + '\n')
		cswrs[env] += 1
print 'Siginificantly condifent events detected per environment : %d / %d' % (cswrs[0], cswrs[1])
fswrs1.close()
fswrs2.close()

if argv[1] != '-':
	dump_stats(preds)

exit(0)

#andir = os.path.dirname(argv[1]) + 'analyses/'
#confidences = [float(f) for f in open(andir + 'confidences.txt') if len(f) > 0]
# analyze confidences
#plot_ecdf(confidences, 0)

# plot additional confidences for comparison
if len(argv) > 5:
	confs = np.array([float(f) for f in open(argv[2]) if len(f) > 0])
	#clsfs = np.array([float(f) for f in open(os.path.dirname(argv[2]) + '/clsf.txt') if len(f) > 0])
	
	#confs = confs[clsfs >= 0]
	plot_ecdf(confs, 1)

#plt.grid()
#daylab = 'CON-20: '
#plt.legend([daylab + 'SWRs', daylab + 'learning'])
#plt.show()
