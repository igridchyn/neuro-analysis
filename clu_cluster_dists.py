#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *
import struct
from scipy.stats import entropy

def gau_kl(pm, pv, qm, qv):

   """
   Kullback-Liebler divergence from Gaussian pm,pv to Gaussian qm,qv.
   Also computes KL divergence from a single Gaussian pm,pv to a set
   of Gaussians qm,qv.
   Diagonal covariances are assumed.  Divergence is expressed in nats.
   """

   if (len(qm.shape) == 2):
       axis = 1
   else:
       axis = 0

   # Determinants of diagonal covariances pv, qv
   dpv = pv.prod()
   dqv = qv.prod(axis)
   # Inverse of diagonal covariance qv
   iqv = 1./qv
   # Difference between means pm, qm
   diff = qm - pm

   return (0.5 *
           (np.log(dqv / dpv)            # log |\Sigma_q| / |\Sigma_p|
            + (iqv * pv).sum(axis)          # + tr(\Sigma_q^{-1} * \Sigma_p)
            + (diff * iqv * diff).sum(axis) # + (\mu_q-\mu_p)^T\Sigma_q^{-1}(\mu_q-\mu_p)
            - len(pm)))                     # - N


# output distances from given cluster to the other

if len(argv) < 4:
	print 'USAGE: (1)<number of features> (2)<tetrode number> (3)<first base name> ... (N)<last base name>'
	exit(0)

# 1. read all fet
# 2. endless loop:
#    - get cluster number
#    - load clu
#    - output closest clusters

NFET = int(argv[1])
TETR = int(argv[2])
fets = []
ts = []
BASES = argv[3:]

for base in BASES:
    f = open(base + '.fetb' + '.' + str(TETR))
    # N float features, 4 float special features, int time

    fmt = (NFET + 4) * 'f' + 'i'
    spike_size = 4 * (NFET + 4 + 1)

    while True:
        spikebin = f.read(spike_size)

        if not spikebin:
            break

        fet = struct.unpack(fmt, spikebin)
        fets.append(fet[:NFET])
        ts.append(fet[-1])

fet = np.array(fets)

print fet.shape

# build map time -> features
mtf = {}
for i in range(len(ts)):
    mtf[ts[i]] = fet[i,:]

# read clu range -> calculate cross-clust dists
while True:
    s = raw_input('Enter cluster range and target cluster, separated with spaces:')
    if len(s) < 5:
            exit(0)

    ws = s.split(' ')

    # read clu/res

    clu = []
    res = []
    for base in BASES:
        clu.extend([int(c) for c in open(base + '.clu')])
        res.extend([int(r) for r in open(base + '.res')])

    # build clusters:
    # start / end /  reference
    clu_s = int(ws[0])
    clu_e = int(ws[1])
    clu_r = int(ws[2])

    print 'Start/end/ref clu:', clu_s, clu_e, clu_r

    clus = {}
    for c in range(clu_s, clu_e + 1):
        clus[c] = []

    for i in range(len(clu)):
        if clu[i] >= clu_s and clu[i] <= clu_e:
            #print i, clu[i], res[i]
            clus[clu[i]].append(mtf[res[i]])

    # DEBUG
    #for c in clus:
    #    print c, len(clus[c])

    # calculate distances from reference cluster to the other ones
    means = {}
    covs = {}
    for c in clus:
        #print c
        if type(clus[c]) != type(0) and len(clus[c]) > 0:
            means[c] = np.mean(clus[c], 0)
            #print len(clus[c])
            covs[c] = np.cov(np.transpose(clus[c]))
#        else:
            #print 'Empty cluster:', c

    cd = []
    dd = []

    for c in clus:
        if c not in means or c == clu_r:
            continue
            #dist = gau_kl(means[c], means[clu_r], covs[c], covs[clu_r])
            #dist = entropy(clus[c], clus[clu_r])

        cv1 = covs[c]
        cv2 = covs[clu_r]
        m1 = means[c]
        m2 = means[clu_r]
        k = len(means[c])

        #print np.transpose(m1).shape

        dist = 0.5 * (np.trace(np.linalg.inv(cv2) * cv1) + (m2-m1).dot(np.linalg.inv(cv2)).dot(m2-m1) - k + np.log(np.linalg.det(cv2) / np.linalg.det(cv1)))

        #print dist
        #print 'KL between %d and %d = %.2f' % (c, clu_r, dist)

        cd.append(c)
        dd.append(dist)

    so = np.argsort(dd)
    for i in range(len(dd)):
        print 'KL between %d and %d = %.2f' % (cd[so[i]]-clu_s+1, clu_r-clu_s+1, dd[so[i]])

