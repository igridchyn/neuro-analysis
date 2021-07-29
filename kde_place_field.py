#!/usr/bin/env python
from sys import argv
from scipy.stats import gaussian_kde
from tracking_processing import *
from matplotlib import pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity
from math import log

def KL(a, b):
	sm = 0
	for i in range(len(a)):
		if b[i] > 0 and a[i] > 0:
			sm += a[i] * log(a[i] / b[i])

	return sm

def JensenShannon(a, b):
	return 0.5 * (KL(a,b) + KL(b,a))

def spike_positions(clu, res, whl, speed, cluster, f, t):

	print len(clu), len(res)

	spike_pos = []

	for i in range(len(res)):
		if res[i] < f or res[i] > t:
			continue

		if clu[i] == cluster:
			wi = res[i] / 480
			spos = whl[wi]
			if spos > 0 and speed[wi] > SPEED_THOLD:
				spike_pos.append(spos)
	spar = np.array(spike_pos)

	return spar

if len(argv) < 8:
	print 'Usage: (1)<basename1 for clu/res/whl> (2)<basename2> (3)<cluster id> (4)<s1 from> (5)<s1 to> (6)<s2 from> (7)<s2 to>'
	print 'KDE place fields and their comparison - in 2 sessions?'
	exit(0)

s1f = int(argv[4])
s1t = int(argv[5])
s2f = int(argv[6])
s2t = int(argv[7])

basename = argv[1]
basename2 = argv[2]

clu1 = [int(c) for c in open(basename + 'clu')]
res1 = [int(r) for r in open(basename + 'res')]
whl1 = whl_to_pos(open(basename + 'whl.linear'), True)
speed1 = whl_to_speed(whl1)

clu2 = [int(c) for c in open(basename2 + 'clu')]
res2 = [int(r) for r in open(basename2 + 'res')]
whl2 = whl_to_pos(open(basename2 + 'whl.linear'), True)
speed2 = whl_to_speed(whl2)

#plt.scatter([p[0] for p in spike_pos], [p[1] for p in spike_pos])
#plt.show()

cluster = int(argv[3])

SPEED_THOLD = 4

for cluster in range(1, 200):

	spar = spike_positions(clu1, res1, whl1, speed1, cluster, s1f, s1t)
	spar2 = spike_positions(clu2, res2, whl2, speed2, cluster, s2f, s2t)
	print spar.shape

	if len(spar) < 50 or len(spar2) < 50:
		print 'ERROR: one of the session has less than 50 spikes'
		continue

	bw = 10
	#kernel = gaussian_kde(spar)
	kde_skl = KernelDensity(bandwidth = bw)
	kde_skl.fit(spar)
	kde_skl2 = KernelDensity(bandwidth = bw)
	kde_skl2.fit(spar2)

	xmin = min(spar[0, :])
	xmax = max(spar[0, :])
	ymin = min(spar[1, :])
	ymax = max(spar[1, :])
	xd = xmax - xmin
	yd = ymax - ymin
	xmin -= xd/2
	xmax += xd/2
	ymin -= yd/2
	ymax += yd/2

	xmin = 70
	xmax = 360
	ymin = 20
	ymax = 200

	X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:50j]
	positions = np.vstack([X.ravel(), Y.ravel()]).transpose()
	print positions.shape
	#Z = np.reshape(kernel(positions).T, X.shape)

	Z = np.reshape(np.exp(kde_skl.score_samples(positions)).T, X.shape)
	Z2 = np.reshape(np.exp(kde_skl2.score_samples(positions)).T, X.shape)

	print 'map shape: ', Z.shape

	psz = 3

	#fig = plt.figure()
	fig, (ax1, ax2) = plt.subplots(1,2)
	#ax = fig.add_subplot(111)

	# 2D
	ax1.imshow(np.rot90(Z), cmap=plt.cm.jet, extent=[xmin, xmax, ymin, ymax], interpolation='none')
	ax1.scatter(spar[:,0], spar[:,1], color='w', s=psz)

	# 1D
	#print Z
	#ax1.plot(range(Z.shape[1]), Z[0,:])

	# ax.plot(m1, m2, 'k.', markersize=2)
	ax1.set_xlim([xmin, xmax])
	ax1.set_ylim([ymin, ymax])

	#ax = fig.add_subplot(121)
	ax2.imshow(np.rot90(Z2), cmap=plt.cm.jet, extent=[xmin, xmax, ymin, ymax]) #plt.cm.gist_earth_r
	ax2.scatter(spar2[:,0], spar2[:,1], color='w', s=psz)
	# ax.plot(m1, m2, 'k.', markersize=2)
	ax2.set_xlim([xmin, xmax])
	ax2.set_ylim([ymin, ymax])

	#Z /= sum(Z)
	#Z2 /= sum(Z2)
	js_dist1 = JensenShannon(Z[0:Z.shape[0]/2,:].flatten(), Z2[0:Z2.shape[0]/2,:].flatten())
	js_dist2 = JensenShannon(Z[Z.shape[0]/2:,:].flatten(), Z2[Z2.shape[0]/2:,:].flatten())
	print 'Distances: %.3f / %.3f' % (js_dist1, js_dist2)

	fig.set_size_inches(45, 10.5, forward=True)
	plt.show()
