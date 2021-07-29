#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
from tracking_processing import *
from iutils import *

#========================================================================================================================================================
def read_trials(path):
        trials = []
        for line in open(path):
                if len(line) < 3:
                        continue
                trials.append([int(w) for w in line.split(' ')])
        return trials
#========================================================================================================================================================
def trial_environments(whl, trials):
        envs = []
	EPS = 0.001
        for t in trials:
                # find first valid (> EPS) position in the whl and see where it lies
                i = t[0] / 480 + 1
                iend = t[1] / 480 + 1
                while i < iend and whl[i][0] < EPS:
                        i += 1
                envs.append(int(whl[i][0] > 200))
        return envs
#========================================================================================================================================================
def first_trials(trials, envs, n):
	# final array of intervals
	intervals = []
	# return array of intervals, covering the first n trials in each environment
	e = [0, 0]
	i = 0
	# start of the next interval
	start = 0
	while (e[0] < n) or (e[1] < n):
		# find start
		while e[0] == n and envs[i] == 0 or e[1] == n and envs[i] == 1:
			i += 1

		start = trials[i][0]
		# e[envs[i]] += 1

		# find end
		while e[0] < n and envs[i] == 0 or e[1] < n and envs[i] == 1:
			e[envs[i]] += 1
			i += 1

		end = trials[i-1][1]
		
		intervals.append([start, end])	
	print 'Trials, envs, intervals: '
	print trials
	print envs
	print intervals

	return intervals
#========================================================================================================================================================
def last_trials(trials, envs, n):
	# final array of intervals
	intervals = []
	# return array of intervals, covering the first n trials in each environment
	e = [0, 0]
	i = len(trials) - 1
	# start of the next interval
	start = 0
	while (e[0] < n) or (e[1] < n):
		# find start
		while (e[0] == n) and (envs[i] == 0) or (e[1] == n) and (envs[i] == 1):
			i -= 1

		end = trials[i][1]
		# e[envs[i]] += 1

		# find end
		while (e[0] < n) and (envs[i] == 0) or (e[1] < n) and (envs[i] == 1):
			e[envs[i]] += 1
			i -= 1

		start = trials[i+1][0]
		
		intervals.insert(0, [start, end])

	print 'Trials, envs, intervals: '
	print trials
	print envs
	print intervals
	
	return intervals

if len(argv) < 5:
	print 'Usage: (1)<base path (ending with .)> (2)<time window in ms> (3)<time frame start or - or tf<trial> or tl<trial> > (4)<time frame end> (5)<OCC MAP - AS FILTER> [ (6)<g1x> (7)<g1y> (8)<g2x> (9)<g2y>]'
	print 'Output: *.frs_e1/2, *.corrs_e1/2 files - firing rate and correlations per environment'
	exit(0)

print 'WARNING: using old about.txt'
argv = resolve_vars(argv, True)

occmap = np.loadtxt(argv[5])
BS = 6.0
print 'WARNING: bin size for occupancy filter map assumed to be 6'
print '		occmap shape:', occmap.shape

goalmode = False
gpref = ''
grad = 20
if len(argv) > 6:
	# gpref = 'NOSB_ST4_OCC5.'
	gpref = 'NOSB_ST4_OCC5.'
	
	goalmode =  True
	g1x = float(argv[6])
	g1y = float(argv[7])
	g2x = float(argv[8])
	g2y = float(argv[9])
	print 'WARNING: GIVEN COORDINATES !!! EXCLUDED !!!, COORDINATES: %d %d; %d %d' % (g1x, g1y, g2x, g2y)

print 'WARNING: FILE NAME SUFFIX HARD-CODED:', gpref

base = argv[1]
win = int(argv[2]) * 24

# whl = whl_to_pos(open(base + 'whl.scaled'), False)
print 'WARNING: using unscaled whl'
whl = whl_to_pos(open(base + 'whl'), False)
clu = [int(c) for c in open(base + 'clu')]
res = [int(r) for r in open(base + 'res')]
speed = whl_to_speed(whl)
ST = 4
print 'WARNING: ST = 4'

trialmode = False
if argv[3] == '-':
	tstart = 0
elif argv[3][0] == 't':
	trialmode = True
	trials = read_trials(base +  'whl.trials')
	envs = trial_environments(whl, trials)
	if argv[3][1] == 'f':
		tints = first_trials(trials, envs, int(argv[3][2:]))
	elif argv[3][1] == 'l':
		tints = last_trials(trials, envs, int(argv[3][2:]))
	else:
		print 'WRONG TRIAL SIGNATURE'
		exit(2344)
else:
	tstart = int(argv[3])

# otherwise defined before
if not trialmode:
	if argv[4] == '-':
		tend = res[-1]
	else:
		tend = int(argv[4])

nclu = np.max(clu)

ifrs1 = []
ifrs2 = []
for i in range(nclu):
	ifrs1.append([])
	ifrs2.append([])

# current window end
wend = 0
i = 0
while res[i] < (tints[0][0] if trialmode else tstart):
	i += 1
wend = (res[i] / win) * win
istart = i

# current ifr (depending on current environment)
cifr = ifrs1
# current environment : 0/1
curenv = 0
SEPX = 200
print 'WARNING: environment border = 200'
include_current = False
speed_ok = False
# current interval in tints
curint = 0
for i in range(istart, len(res)):
	if res[i] > (tints[-1][1] if trialmode else tend):
		break

	# skip until next interval reached
	if trialmode:
		if res[i] > tints[curint][1]:
			if res[i] > tints[curint + 1][0]:
				curint += 1
				# ?
				include_current = False
			else:
				continue

	if res[i] > wend:
		# new entry
		if (not include_current or not speed_ok or not occ_pass) and len(cifr[0]) > 0:
			# just set last values to 0 and continue
			for c in range(nclu):
				cifr[c][-1] = 0
		else:
			for c in range(nclu):
				cifr[c].append(0)

		include_current = True
		speed_ok = False
		occ_pass = False
		wend += win

	if res[i] / 480 >= len(whl):
		print 'WHL end reched at res[i] = ', res[i], ' stop'
		break

	pos = whl[res[i] / 480]

	if speed[res[i] / 480] > ST:
		speed_ok = True

	# this can be any of 4 : goal / SB + restrictied / prohibited
	if goalmode and pos[0] > 0.1 and pos[0] < 1000:
		d1 = distance([g1x, g1y], pos)	
		d2 = distance([g2x, g2y], pos)	
		if d1 < grad or d2 < grad:
			include_current = False

	# check if position passes the occupancy filter - occupancy map from end of new learning session
	bposx = int(round(pos[0] / BS))
	bposy = int(round(pos[1] / BS))
	if pos[0] > 0.1 and pos[0] < 1000 and occmap[bposy, bposx] >= 0:
		occ_pass = True
		# if ANY-OUT logic is required, uncomment next line
		# include_current = False

	# check for environment swithc; optionally - take the session files ...
	if pos[0] > 0.1 and pos[0] < 1000:
		if pos[0] < SEPX and curenv == 1:
			curenv = 0
			cifr = ifrs1
			for c in range(nclu):
				cifr[c].append(0)
		if pos[0] >= SEPX and curenv == 0:
			curenv = 1
			cifr = ifrs2
			for c in range(nclu):
				cifr[c].append(0)


	# print clu[i], len(cifr)
	cifr[clu[i] - 1][-1] += 1
	
# compute correlations env-wise, display both
ifrs1 = np.array(ifrs1)
ifrs2 = np.array(ifrs2)
corr1 = np.corrcoef(ifrs1)
corr2 = np.corrcoef(ifrs2)

for c in range(nclu):
	corr1[c,c] = 0
	corr2[c,c] = 0

if gpref == '' and ST > 0:
	gpref = 'st%d_' % ST

np.savetxt(base + gpref + 'corr_e1', corr1)
np.savetxt(base + gpref + 'corr_e2', corr2)

frse1 = []
frse2 = []
nt1 = ifrs1.shape[1]
nt2 = ifrs2.shape[1]

print 'Number of population vectors : %d / %d' % (nt1, nt2)

for c in range(nclu):
	frse1.append(np.sum(ifrs1[c, :]) / float(nt1) * 24000 / float(win))
	frse2.append(np.sum(ifrs2[c, :]) / float(nt2) * 24000 / float(win))

np.savetxt(base + gpref + 'frs_e1', frse1)
np.savetxt(base + gpref + 'frs_e2', frse2)


#f, (ax1, ax2) = plt.subplots(1, 2)
#ax1.imshow(corr1, interpolation = 'nearest')
#ax2.imshow(corr2, interpolation = 'nearest')
#plt.show()
