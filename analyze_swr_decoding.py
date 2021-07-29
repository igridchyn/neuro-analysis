#!/usr/bin/env python

import os
import glob
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from numpy import log, exp
import random

class Swrdec:
	# SWR id, time relative, confidence 1/2, max x, max y, lieklihood 1/2
	def __init__(self, swrid, tr, mx1, my1, mx2, my2, l1, l2):
		self.swrid = swrid
		self.tr = tr
		self.mx1 = mx1
		self.my1 = my1
		self.mx2 = mx2
		self.my2 = my2
		self.l1 = l1
		self.l2 = l2

	def conf(self):
		return abs(self.l1 - self.l2)

	def ldiff(self):
		return self.l1 - self.l2
	
#=================================================================================================================================

if len(argv) < 5:
	print 'Arguments: (1)<swrdec file with LFPO-output of SWR decoding> (2)<percentage of most confident events (in each environment) to show> (3)<swr timestamp file> (4)<confidence threshold for occupancy analysis>'
	print 'Plot: occupancy map for decoded positions in sleep, trajectories for the most confdent events (size ~ confidence)'
	exit(0)

print 'WARNING: POLY FIT NOT PERFORMED, NEED CONFIDENCES INSTEAD OF PROBABILITIES'
	
f = open(argv[1])

swrs = [int(t) for t in open(argv[3])]
nswr = len(swrs)

BSIZE = 1
NBX = 320
NBY = 1
dpos = np.zeros((NBX, NBY))
CPERC = float(argv[2])
CPLOTTHOLD = float(argv[4])

print 'NBX=%d, NBY=%d, BSIZE=%.2f' % (NBX, NBY, BSIZE)

sds = []

ne1 = 0
ne2 = 0
envs = []
econfs1 = []
econfs2 = []
for line in f:
	w = line.split(' ')
	if len(w) < 5:
		continue

	bx1 = round(int(w[6]) / BSIZE)
	by1 = round(int(w[7]) / BSIZE)
	bx2 = round(int(w[8]) / BSIZE)
	by2 = round(int(w[9]) / BSIZE)

	if bx1 >= NBX or bx2 >= NBX:
		continue

	# [4/5] are sums

	c1 = float(w[2])
	c2 = float(w[3])
	conf = c1 - c2

	if abs(conf) > CPLOTTHOLD:
		if c1 > c2:
			ne1 += 1
			dpos[bx1, by1 - 1] += 1
			envs.append(0)
			econfs1.append(c1 - c2)
		else:
			ne2 += 1
			dpos[bx2, by2 - 1] += 1
			envs.append(1)
			econfs2.append(c2 - c1)

	swrid = int(w[0])
	sds.append(Swrdec(swrid, swrs[swrid] - int(w[1]), bx1, by1, bx2, by2, c1, c2))

print 'Environments balance: %d / %d' % (ne1, ne2)
plt.figure()
plt.imshow(dpos, interpolation = 'none')
plt.show()
	
# trajectories for the most confident swrs
avgconf = [[] for i in range(nswr)]
absconfs = []
for sd in sds:
	avgconf[sd.swrid].append(sd.l1 - sd.l2)
	absconfs.append(sd.conf())

# print 95% level of window-wise confidence
if len(argv) > 5:
	CLEV = float(argv[5])
else:
	CLEV = 0
print '95%% level of window-wise confidence: %.2f' % np.sort(absconfs)[95/100.0 * len(absconfs)]
print 'Fraction >%.2f: %.3f' % (CLEV, sum(np.array(absconfs) > CLEV) / float(len(absconfs)))

avgconf = [np.mean(a) for a in avgconf]
print '95%% level of SWR-average ldiff: %.2f' % np.sort(avgconf)[95/100.0 * len(avgconf)]
print 'Fraction >%.2f: %.3f' % (CLEV, sum(np.array(avgconf) > CLEV) / float(len(avgconf)))
print '5%% level of SWR-average ldiff: %.2f' % np.sort(avgconf)[5/100.0 * len(avgconf)]
print 'Fraction <%.2f: %.3f' % (CLEV, sum(np.array(avgconf) < CLEV) / float(len(avgconf)))

CTHOLD1 = np.sort(avgconf)[CPERC / 100.0 * len(avgconf)]
CTHOLD2 = np.sort(avgconf)[(100.0-CPERC) / 100.0 * len(avgconf)]
print 'Threshold for given percentile (%.2f) = %.2f / %.2f' % (CPERC, CTHOLD1, CTHOLD2)

print 'Window-wise confidence mean / std: %.2f / %.2f' % (np.mean(absconfs), np.std(absconfs))

# swr windows by swr id
sdbyid = [[] for i in range(nswr)]
for sd in sds:
	sdbyid[sd.swrid].append(sd)

plt.figure()
plt.hist(avgconf, 50)
plt.show()

pref = 'swr_trajectories/'
if not os.path.isdir('swr_trajectories'):
	os.mkdir('swr_trajectories')

random.seed(123457623)

print 'WARNING! ONLY WINDOWS WITH CONFIDENCE > %.2f WILL BE USED' % CLEV
for i in range(nswr):
	if avgconf[i] > CTHOLD1 or avgconf[i] < CTHOLD2:
		tsd = sdbyid[i]
		
		env = 0 if avgconf[i] > 0 else 1
		print 'Environment %d is expressed more (mean conf = %.2f)' % (env, avgconf[i])

		xs = []
		ys = []
		ps = []
		ts = []

		xsa=[]
		psa=[]
		plot_alt = True

		dpos = 0
		dposa = 0

		tmin = tsd[0].tr
		for sd in tsd:
			wconf = sd.ldiff() if env == 0 else -sd.ldiff()
			if wconf < CLEV:
				continue

			sf = 200
			sdi = 100

			xs.append(sd.mx1 if env == 0 else sd.mx2) # + random.random() * 4)
			#ys.append(sd.my + random.random() * 4)
			ys.append(float(sd.tr))
			#ps.append(sd.ldiff() if env == 0 else -sd.ldiff())
			ps.append(sd.l1 if env == 0 else sd.l2)
			ts.append(float(sd.tr))
			
			xsa.append(sd.mx2 if env == 0 else sd.mx1)
			psa.append(sd.l2 if env == 0 else sd.l1)

			if len(xs) > 1:
				dpos += abs(xs[-1] - xs[-2])
				dposa += abs(xsa[-1] - xsa[-2])

		ps = [exp(p/sdi) for p in ps]
		psa = [exp(p/sdi) for p in psa]
		meanps = np.mean(ps)
		meanpsa = np.mean(psa)
		totf = 75
		ps = [p / meanps * totf for p in ps]
		psa = [p / meanpsa * totf for p in psa]

		if len(xs) == 0:
			print 'WARNING: EMPTY SEQUENCE'
			continue

		if len(xs) < 6:
			print 'WARNING: SHORT SEQUENCE NOT SHOWN'
			continue

		plt.figure(figsize=(20, 12))
		dpos /= len(xs) - 1
		dposa /= len(xs) - 1

		#polyfit
		ps = np.array(ps)
		ys = np.array(ys)
		xs = np.array(xs)

		ps_pos = ps[ps > 0]

		#polyfit = np.polynomial.polynomial.polyfit(ys[ps > 0], xs[ps > 0], 2, w=ps_pos)
		#polyfit1 = np.polynomial.polynomial.polyfit(ys[ps > 0], xs[ps > 0], 1, w=ps_pos)
		#pres = np.polynomial.polynomial.polyfit(ys, xs, 2, w=ps, full=True)
		#pfit = [(polyfit[0] + polyfit[1]*x + polyfit[2]*x**2) for x in ys]
		#pfit1 = [(polyfit1[0] + polyfit1[1]*x) for x in ys]
			
		plt.plot(xs, ys)

		#plt.plot(pfit, ys, lw=3)
		#plt.plot(pfit1, ys, lw=3)

		plt.scatter(xs, ys, s = ps, c=ts)
		plt.title('SWR %d, time = %d, env=%d, mean pos change = %.2f / %.2f\n%s' % (i, sd.tr, env, dpos, dposa, argv[1]))
		plt.xlim(0, NBX)
		#plt.ylim(0, NBY + 5)

		if plot_alt:
			plt.plot(xsa, ys)
			plt.scatter(xsa, ys, s = psa, c=ts)
			
		plt.colorbar()
		plt.show()








