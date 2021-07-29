#!/usr/bin/env python

import numpy as np
from tracking_processing import whl_to_speed, whl_to_pos
from sys import argv
from sklearn import svm
from sklearn.externals import joblib
from numpy import log, sqrt, abs
from matplotlib import pyplot as plt
from imath import gaussian
from iutils import *
from sklearn import manifold
from sklearn.metrics import euclidean_distances
import os

def whl_to_env(whl):
	return int(whl[0] > envborder)

#==============================================================================================================
if len(argv) < 12:
	print 'Usage: ' + argv[0] + ' (1)<whl_file> (2)<dir with all.clu/res> (3)<speed threshold> (4)<FR threshold> (5)<normalize IFRs> (6)<smooth IFRs> (7)<model save path> (8)<s/l> (9)<output dump path> (10)<fixed spike number of 0 for fixed window> (11)<envborder>'
	print 'BUILD / RUN POPULATION-VECTOR BINARY SVC FOR ENVIRONMENT'
	exit(0)

if argv[8] not in ['s', 'l']:
	print 'Last parameter = s or l'
	exit(1)

whl = whl_to_pos(open(argv[1]), True)
speed = whl_to_speed(whl)

envborder = int(argv[11])

clu = [int(c) for c in open(argv[2] + 'all.clu') if len(c) > 0]
res = [int(r) for r in open(argv[2] + 'all.res') if len(r) > 0]

# filter cells based on mean firing rate
# TODO : skip first 15 minutes ...
# TODO : train on fixed spike number !!!

#cexclude = [2, 6, 30, 52, 53, 60, 61, 76, 83, 84, 91, 92, 94, 95, 97, 100] + [13, 16, 36, 58, 59, 70, 71, 86, 87]
cexclude = []
print 'WARNING: HARD-CODE EXCLUDE CELLS' + str(cexclude)

maxt = res[-1]

# clu = np.array(clu)
ncell = max(clu)

cmap = [-1] * (ncell + 1)

cused = 0
FRTHOLD = float(argv[4])
FRHIGHTHOLD = 10
for c in range(1, ncell + 1):
	afr = clu.count(c)/float(maxt) * 24000
	print 'Average firing rage of cell %d = %.2f Hz' % (c, afr)
	if afr > FRTHOLD and afr < FRHIGHTHOLD and not c in cexclude:
		cmap[c] = cused
		cused += 1

print '%d cells will be used for classifier' % cused

# find staring position
TSTART = 21600000
print 'Start time = %d' % TSTART
#TEND = 43200000
TEND = res[-200]
print 'End time = %d' % TEND
TENV = (TEND - TSTART) / 2
WIN = 2400
print 'Window = %d' % WIN
resi = 0
while (res[resi] < TSTART):
	resi += 1

print 'Starting res position = %d' % resi

# collect population vectors in fixed windows
# TODO !!! plot with distance transform to 2/3 dimensions

popvecs = []
env = []
SPTHOLD = float(argv[3])
lastwin = TSTART
envb = 0
SN = int(argv[10])
if SN > 0:
	print 'Predicting from fixed spike number : %d' % SN
else:
	print 'Predicting from fixed window: %d' % WIN

while res[resi] < TEND:
	popvec = np.zeros((cused, 1))
	
	if SN == 0:
		while res[resi] < lastwin + WIN:
			c = clu[resi]
			if cmap[c] >= 0:
				popvec[cmap[c]] += 1
			resi += 1
	else:
		resi_start = resi
		i = resi	
		#for i in range(resi, resi + SN):
		spikes = 0
		while i < len(clu) and spikes < SN:
			c = clu[i]
			if cmap[c] >= 0:
				spikes += 1
				popvec[cmap[c]] += 1
			i += 1
		#resi += SN
		resi = i
		#WIN = res[resi] - res[resi - SN]
		WIN = res[resi] - res[resi_start]

	whli = (lastwin + WIN/2) / 480
	if speed[whli] > SPTHOLD:
		popvecs.append(popvec)
		# print popvec
		e = whl_to_env(whl[whli])
		env.append(e)

		# detect start of another env
		# env > 0
		if envb == 0 and res[resi] > 43200000:
			envb = len(env)

	lastwin += WIN

print env

print 'Collected %d population vectors' % len(popvecs)
print 'Environments occupacy: %d / %d' % (env.count(0), env.count(1))
print 'Env. starting at: %d' % envb

# build classifier: LDA / SVM / Logistic Regression
popvecs = np.array(popvecs)[:,:,0]
env = np.array(env)
print popvecs.shape
print env.shape

base = argv[9]

# NORMALIZE FIRING RATES
NORMALIZE = bool(int(argv[5]))
if NORMALIZE:
	fnorm = open(base + 'pop.norm', 'w')
	print 'Normalize population vectors'
	for c in range(0, cused):
		mn = np.mean(popvecs[:, c])
		popvecs[:, c] -= mn
		std = np.std(popvecs[:, c])
		popvecs[:, c] /= std
		fnorm.write('%f %f\n' % (mn, std))
	fnorm.close()

# ??? SMOOTH FRS ???
SMOOTH = bool(int(argv[6]))
if SMOOTH:
	print 'Smooth popelation vectors'
	for c in range(0, cused):
		# 7 / 2 - 99.88 %
		popvecs[:, c] = np.convolve(popvecs[:, c], gaussian(7, 2), mode = 'same')

N = env.shape[0]

#itrain = range(0, envb/2) + range(envb, envb + (N-envb)/2)
#itest = range(envb/2, envb) + range(envb + (N-envb)/2, N)

# CAREFUL WITH SMOOTHING
if not SMOOTH:
	itrain = range(0, N, 2)
	itest = range(1, N, 2)
else:
# if envb == <start of post>
	itrain = range(0, envb)
	itest = range(envb, N)

print 'Train/test split : %d / %d' % (len(itrain), len(itest))

# linear - simpler, but not very nice distribution
if argv[8] == 's':
	print 'Save model under ' + argv[9] + argv[7]
	clf = svm.SVC(kernel='rbf', probability = False)
	clf.fit(popvecs[itrain,:], env[itrain])
else:
	print 'Load model from ' + argv[7]
	clf = joblib.load(argv[9] + argv[7])


#pprobs = clf.predict_proba(popvecs[itest,:])
pprob = clf.decision_function(popvecs[itest,:])
prediction = clf.predict(popvecs[itest,:])
#confs = (log(pprobs[:,0]) - log(pprobs[:,1]))
confs = []
for i in range(0, len(prediction)):
	confs.append(pprob[i][0])
	#confs.append((log(pprobs[i,0]) - log(pprobs[i,1])) * max(pprobs[i, 0], pprobs[i, 1]))


# dump population vectors
fpopv = open(base + 'wake_running.popv', 'w')
for pop in popvecs:
	for p in pop:
		fpopv.write('%f ' % p)
	fpopv.write('\n')
fpopv.close()
print 'Written population vectors'


#plt.hist(confs, 50)
#plt.show()

print prediction
print prediction.shape

print 'SVM accuracy: %.4f' % (sum(env[itest] == prediction) / float(len(prediction)))

# dump to analyze accuracy from confidence
exists_or_create(base)
fc = open(base + 'clsf.txt', 'w')
fe = open(base + 'errors.txt', 'w')
fconf = open(base + 'confidences.txt', 'w')

if argv[8] == 's':
	joblib.dump(clf, base + argv[7])

for i in range(0, len(confs)):
	fe.write('10\n')
	fc.write(str(int(prediction[i] == env[itest[i]])) + '\n')
	fconf.write(str(abs(confs[i])) + '\n')
fe.close()
fc.close()
fconf.close()

# dump cmap
fcm = open(base + 'cmap.txt', 'w')
for c in cmap:
	fcm.write('%d\n' % c)
fcm.close()

write_list(env, base + 'envs.txt')

# display MDS transform of the popvecs
mdspath = base + 'mds_smooth' + argv[6] + '_norm' + argv[5] + '.txt'
allpred = clf.predict(popvecs)
if os.path.isfile(mdspath):
	pos = [[float(p.split(' ')[0]), float(p.split(' ')[1])] for p in open(mdspath) if len(p) > 0]
	pos = np.array(pos)
else:
	print 'Start MDS...'
	seed = np.random.RandomState(seed=3)
	similarities = euclidean_distances(popvecs)
	print 'Done similarities'
	# max_iter defgault = 300
	# eps default = 1e-6
	mds = manifold.MDS(n_components = 2, max_iter=300,random_state=seed,dissimilarity='precomputed', n_jobs=-1,n_init=1, eps=1e-6)
	pos = mds.fit(similarities).embedding_
	print 'Done MDS...'
	fmds = open(mdspath, 'w')
	for p in pos:
		fmds.write('%f %f\n' % (p[0], p[1]))
plt.scatter(pos[:,0], pos[:,1], c=env)
plt.show()
