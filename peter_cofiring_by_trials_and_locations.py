#!/usr/bin/env python

from sys import argv
import numpy as np
from math import sqrt

# read: trial intervals (*whl.trial), z-scored ifrs (*frz), sb/goal coords: *.gcoords

def distance(p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def write_corrmat(f, mat):
	for i in range(mat.shape[0]):
		for j in range(i):
			f.write('%d %d %.4f\n' % (i, j, mat[i, j]))

if len(argv) < 3:
	print 'USAGE: (1)<basename for files: .whl.trials, .frz, .whl> (2)<distance threshold>'
	print 'GENERATES correlation matrices for every trials / goals /sb'
	exit(0)

base = argv[1]
dthold = float(argv[2])

f = open(base + '.whl.trials')
trials = []
for line in f:
	ws = line.split(' ')
	if len(ws) > 0:
		trials.append([int(ws[0]), int(ws[1])])

print trials

frs = []
fi = open(argv[1] + '.frz')
for line in fi:
	ws = line.split(' ')
	if len(ws) > 0:
		frs.append([float(fr) for fr in ws if len(fr) > 0 and fr != '\n'])

fwhl = open(argv[1] + '.whl')
whl = []
for line in fwhl:
	ws = line.split(' ')
	if len(ws) > 0:
		whl.append([float(ws[0]), float(ws[1])])

print '%d tracking entries loaded' % len(whl)
print '%d population vectors loaded' % len(frs)

ncell = len(frs[0])
# collect vectors for a trial until it's over => compute correlation matrix
dt = 2000 # samples @ 20 kHz

# read goal coords
gcoords = []
for line in open(argv[1] + '.gcoords'):
	ws = line.split(' ')
	if len(ws) > 1:
		gcoords.append([float(ws[0]), float(ws[1])])
print 'Loaded SB/Goal coords: ', gcoords

# population vectors for: SB, GOAL1-4
tprev = 0
# concatenated cross-trial corerlation matrix
tcmcorr = np.zeros((1,1))

fout = open(base + '_r' + str(dthold) + '.corrs', 'w')

for trial in trials:
	# population vector for start box (1st) and 4 goals
	popvecs = [[], [], [], [], []]

	# make matrix out of range of lists
	# for all population vectors from previous end to start of trial
	for fri in range(tprev / dt, trial[1] / dt):
		whli = int(fri*dt / 512.0)
		# position at this time
		pos = whl[whli]
		for g in range(len(gcoords)):
			if distance(gcoords[g], pos) < dthold:
				popvecs[g].append(frs[fri])
				break

	pvlens = [len(popvecs[i]) for i  in range(len(popvecs))]
	print 'Collected population vectors for SB/goals: ', pvlens
	
	tprev = trial[1]
	
	# compute correlation for each goal location / SB
	for g in range(len(popvecs)):
		if len(popvecs[g]) > 0:
			popmat = np.transpose(np.array(popvecs[g]))
			mcorr = np.corrcoef(popmat)
			print 'Corr mat size:', mcorr.shape
			# print mcorr
		else:
			print 'WARNING: no population vectors for goal %d collected at trial ' % g, trial
			mcorr = np.zeros((ncell, ncell))

		write_corrmat(fout, mcorr)

		if g == 0:
			# concatenated correlation matrix
			cmcorr = mcorr
		else:
			cmcorr = np.concatenate((cmcorr, mcorr))

	if tcmcorr.shape[0] == 1:
		tcmcorr = cmcorr
	else:
		tcmcorr = np.concatenate((tcmcorr, cmcorr))

print 'Shape of overall concatenated correlation matrix: ', tcmcorr.shape
