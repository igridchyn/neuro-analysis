#!/usr/bin/env python

import os
import glob
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from numpy import log, exp

#=======================================================================================================================================================================================================
def confidence(mat):
	nby = mat.shape[0] / 2
	mx1 = np.max(mat[:nby,:])
	mx2 = np.max(mat[nby:,:])
	return abs(mx1 - mx2), mx1, mx2 # * max(mx1, mx2)
#=======================================================================================================================================================================================================

if len(argv) < 9:
	print 'Usage: ' + argv[0] + ' (1)<base path to decoded position dumps> (2)<swr_path> (3)<[l]oad or [s]ave> (4)<dump filename (added to base)> (5)<significance level> (6)<confidence baseline> (7)<likelihood bin (30 bins total)> (8)<confidence bin (30 bins total)>'
	exit(0)

base = argv[1]
swrs = [int(s) for s in open(argv[2]) if len(s) > 0]
print 'Loaded %d swrs' % len(swrs)

swi = 0

# 120
nconf = 400

confs = [0] * nconf
confcounts = [0] * nconf
aconfs = []
for i in range(0, nconf):
	aconfs.append([])
sconfs = []

avgconfs = []
avgconfs_occ = []

avgconfs1 = [0] * nconf
avgconfs2 = [0] * nconf
avgconfs_occ1 = [0] * nconf
avgconfs_occ2 = [0] * nconf

# distributions of likelihoods
likbin = float(argv[7])
nlikbin = 140
mmlikes1 = np.zeros((nconf, nlikbin))
mmlikes2 = np.zeros((nconf, nlikbin))
likesvs = np.zeros((nlikbin, nlikbin))
confbin = float(argv[8])
nconfbin = 30
confmap = np.zeros((nconf, nconfbin))
twin = 120.0
lshift = 0

domenv = []

load = False
dump = False
if len(argv) > 3:
	if argv[3] == 's':
		dump = True
		fdump = open(argv[1] + argv[4], 'w')
	elif argv[3] == 'l':
		load = True

if load:
	# estimate likelihood and confidence distr

	f = open(argv[1] + argv[4])
	l = f.readline()
	while l and len(l) > 0:
		words = f.readline().split(' ')
		if len(words) < 4:
			break
		totallik = float(words[-1])
		swi = int(words[0])
		time = int(words[1])
		mx1 = float(words[2])# - totallik
		mx2 = float(words[3])# - totallik
		l = f.readline()	

		#mx1 -= totallik
		#mx2 -= totallik

		if swi >= len(avgconfs):
			while swi >= len(avgconfs):
				avgconfs.append([0.0] * nconf)
				avgconfs_occ.append([0.0] * nconf)
				domenv.append([0] * nconf)

		if swi >= len(swrs):
			break

		ind = int(np.round((time - swrs[swi]) / twin) + nconf / 2) # + np.random.rand(1,1)*2) # !!!

		if ind < 0 or ind >= nconf:
			continue

		if abs(mx1) > 10000 or abs(mx2) > 10000:
			print 'Ignore faulty entry: SWR #%d @ %d / %.2f, %.2f' % (swi, time, mx1, mx2)
			continue
	
		bline = float(argv[6]) # 15 for SSI-21/20s
		sconfs.append(mx1 - mx2 + bline)
		conf = abs(mx1 - mx2 + bline)
		confs[ind] += conf
		confcounts[ind] += 1
		aconfs[ind].append(conf)

		# print swi, ind
		avgconfs[swi][ind] += conf # * exp(max(mx1, mx2))
		avgconfs_occ[swi][ind] += 1
		if mx1 > mx2 - bline:
			domenv[swi][ind] -= 1
			#avgconfs1[ind] += (mx1-mx2 + bline)
			#avgconfs1[ind] += mx1 + bline
			#avgconfs_occ1[ind] += 1
		else:
			domenv[swi][ind] += 1
			#avgconfs2[ind] += -(mx1-mx2 + bline)
			#avgconfs2[ind] += mx2
			#avgconfs_occ2[ind] += 1
		avgconfs1[ind] += mx1 + bline
		avgconfs_occ1[ind] += 1
		avgconfs2[ind] += mx2
		avgconfs_occ2[ind] += 1

		lb1 = (mx1 + lshift) / likbin
		if lb1 >= 0 and lb1 < nlikbin:
			mmlikes1[ind, lb1] += 1
		lb2 = (mx2 + lshift) / likbin
		if lb2 >= 0 and lb2 < nlikbin:
			mmlikes2[ind, lb2] += 1

		if lb1 >=0 and lb2 >=0 and lb1 < nlikbin and lb2 < nlikbin and ind in range(45, 60):
			likesvs[lb1, lb2] += 1
		#else:
		#	print lb1, lb2

		cb = conf / confbin
		if cb < nconfbin:
			confmap[ind, cb] += 1

#for i in range(0, nconf):
#	csorted = np.sort(aconfs[i])
#plt.plot(range(tfrom, tto, 10), np.array(confs[fm:to]) / np.array(confcounts[fm:to]), lw=5)
#	# print csorted
#	aconfs[i] = csorted[(100-p) * len(aconfs[i])/100:]
#	confs[i] = np.sum(aconfs[i])
#	confcounts[i] = p * confcounts[i] / 100

# BECAUSE OF THE WILDCARD, ORDER IS NOT ALWAYS CORRECT
while not load and len(glob.glob(base + str(swi) + '_*_0.mat')) > 0:
	pat = glob.glob(base + str(swi) + '_*_0.mat')
	nwin = len(pat)

	#print pat

	# time windows
	for f in pat:
		pred = np.genfromtxt(f)
		conf, mx1, mx2 = confidence(pred)
		# print f
		time = int(f.split('_')[-2])
		#print time
		ind = int(np.round((time - swrs[swi]) / 240.0) + nconf/2)
	
		mn = np.min(pred)
		nby = pred.shape[0] / 2
		pred1 = pred[:nby,:]
		pred2 = pred[nby:,:]
		sm1 = np.sum(pred1[pred1 > mn + 0.1])
		sm2 = np.sum(pred2[pred2 > mn + 0.1])

		if dump:
			fdump.write(str(swi) + ' ' + str(time) + ' ' + str(mx1) + ' ' + str(mx2) + ' ' + str(sm1) + ' ' + str(sm2) + '\n')

		if ind < 0 or ind >= len(confs):
			#print 'Beyond: %d' % ind
			continue

		# print ind
		confs[ind] += conf
		confcounts[ind] += 1
	print '%d windows for SWR #%d at time %d' % (nwin, swi, time)
	swi += 1

	# !!!
	if swi > 1432:
		break
if dump:
	fdump.flush()
	fdump.close()

print 'Mean conf: %f' % np.mean(sconfs)

avgconfs1 = np.array(avgconfs1)
avgconf_occ1 = np.array(avgconfs_occ1)
avgconfs2 = np.array(avgconfs2)
avgconf_occ2 = np.array(avgconfs_occ2)
avgconfs1 /= avgconfs_occ1
avgconfs2 /= avgconfs_occ2

print 'Events per class : %d / %d' % (np.sum(avgconfs_occ1), np.sum(avgconfs_occ2))

# analyze how consistent are the sub-window predictions:
winrange = nconf / 2 - 10
print 'Win range for cnosistency calculation = %d' % winrange
aggmat = np.zeros((winrange*2+1, winrange*2+1))
domenv = np.array(domenv)
wrange = range(nconf/2-winrange, nconf/2+winrange+1)
# for win in range(nconf/2-winrange, nconf/2+winrange+1):
# TODO: for confident only
for i in range(0, swi):
	aggmat[sum(domenv[i][wrange]>0)][sum(domenv[i][wrange]<0)] += 1
#plt.imshow(aggmat, origin='lower')
#plt.show()

p = 100
nswr = len(swrs)
startn = nswr*(100-p)/float(100)
print 'Start from %s in list of sorted confidences' % startn
# take into account only top confident in central bin
avgconfs = np.array(avgconfs)
avgconfs_occ = np.array(avgconfs_occ)
print 'Shape of avgconfs_occ: ' + str(avgconfs_occ.shape)
avgconfs = avgconfs  /  avgconfs_occ
SORTWIN = nconf/2
SORTWINRANGE = 3
print 'Target window : %d with range : %d' % (SORTWIN, SORTWINRANGE)
# print 'Confidences in the target window: ' + str(avgconfs[:, SORTWIN])
# !!! HACK TO SORT
avgconfs[np.isnan(avgconfs)] = -1
itopconf = np.argsort(avgconfs[:, SORTWIN])[startn:]
print 'TOP CONFIDENCES IN THE TARGET WINDOW: ' + str(avgconfs[itopconf, SORTWIN])
print 'itopconf: ' + str(itopconf)
avgconfs = avgconfs[itopconf, :]
print 'Shape of avgconfs after subsampling: ' + str(avgconfs.shape)
print confcounts

# plt.hist(aconfs[nconf/2], 100)
#plt.hist(sconfs, 100)
#plt.show()

#np.set_printoptions(threshold=np.nan)
nswrperwin = np.sum(avgconfs > 0, 0)
print 'Number of swrs per window: ' + str(nswrperwin)
# HACK BACK
avgconfs[avgconfs < 0] = np.nan
avgconfs = np.nansum(avgconfs, 0) / nswrperwin
print 'avngconfs after normalizing by SWR number:'
print avgconfs

fm = 10
to = nconf - 6
tfrom = int(round(-(nconf / 2 - fm) * (twin / 24)))
tto = int(round((to - nconf / 2) * (twin / 24)))
print 'Tfrom / Tto: %d / %d' % (tfrom, tto)
##plt.plot(range(tfrom, tto, 10), np.array(confs[fm:to]) / np.array(confcounts[fm:to]), lw=5)
plt.plot(range(tfrom, tto, 5), avgconfs[fm:to], lw=5,c ='k')
plt.plot(range(tfrom, tto, 5), avgconfs1[fm:to], lw = 5, c='b')
plt.plot(range(tfrom, tto, 5), avgconfs2[fm:to], lw = 5, c='g')
# plt.errorbar(range(tfrom, tto, 10), np.array(confs[fm:to]) / np.array(confcounts[fm:to]), [np.std(np.array(ar)) for ar in aconfs[fm:to]], lw=5)
plt.xlabel('Time relative to the synchrony detection')
plt.ylabel('Mean likelihood')
plt.legend(['Confidence', 'Target environment' , 'Control environment'])
plt.xticks(range(tfrom,tto,60))
siglev = float(argv[5])
#plt.axhline(siglev, color = 'r', lw=4)
plt.axvline(0, color='r', lw=4)
plt.axvline(100, color='g', lw=4)
plt.grid()
plt.title(argv[4])
# plt.savefig('~/resim/SSI-21_Mean_confidence_PSTH.png')
plt.show()

lrange = range(0, nconf, 10)

print likesvs[likesvs > 0]
llmax = np.max(likesvs)
for i in range(nlikbin):
	likesvs[i, i] = llmax
plt.figure()
plt.title('Likelihoods distribution')
plt.xlabel('Max likelihood of ENV1')
plt.ylabel('Max likelihood of ENV2')
plt.imshow(likesvs, interpolation='none', origin='lower')
plt.show()

# plot likes distribution
plt.figure()
yrange = range(0, nlikbin, nlikbin / 6)
for b in range(0, nconf):
	mmlikes1[b, :] /= sum(mmlikes1[b,:])
	mmlikes2[b, :] /= sum(mmlikes2[b,:])
plt.imshow(np.transpose(mmlikes1), interpolation='none', vmin = 0, vmax = 0.1, origin='lower')
plt.title('Likelihoods of environment 1')
plt.xticks(lrange, [i*twin/24.0 - nconf/2*twin/24.0 for i in lrange])
plt.yticks(yrange, [i*likbin - lshift for i in yrange])
plt.show()
plt.imshow(np.transpose(mmlikes2), interpolation='none', vmin = 0, vmax = 0.1, origin='lower')
plt.title('Likelihoods of environment 2')
plt.xticks(lrange, [i*twin/24.0 - nconf/2*twin/24.0 for i in lrange])
plt.yticks(yrange, [i*likbin - lshift for i in yrange])
plt.show()

plt.figure()
for b in range(0, nconf):
	confmap[b, :] /= sum(confmap[b,:])
plt.imshow(np.transpose(confmap), interpolation='none', vmin = 0, vmax = 0.1, origin='lower')
plt.colorbar(orientation = 'horizontal')
plt.title('Confidence distribution')
yrange = range(0, nconfbin, nconfbin / 6)
plt.yticks(yrange, [i*confbin for i in yrange])
plt.xticks(lrange, [i*twin/24.0 - nconf/2*twin/24.0 for i in lrange])
plt.show()

np.save(argv[4] + '.confd', confmap)
np.save(argv[4] + '.lik1', np.transpose(mmlikes1))
np.save(argv[4] + '.lik2', np.transpose(mmlikes2))
