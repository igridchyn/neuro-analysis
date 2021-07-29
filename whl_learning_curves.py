#!/usr/bin/env python

from matplotlib import pyplot as plt
import os 
from sys import argv
from iutils import *
from tracking_processing import *
import numpy as np

#============================================================================================================================================================================
# filter out tracking jumps - temporary changes to distant locations and returns
def filter_jumps(whl):
	# minimal jump to be considered an artefact
	MINJUMP = 20
	# maximal time of a jump, in samples (~50Hz)
	MAXTIME = 500
	# radius of starting point to which the jump has to return
	RETRAD = 30

	# 1. take into account that before jump can be unknown !
	# 2. can tracking start from jump? - rather exception, check manually

	# last known position index
	ilk = 0
	
	for i in range(len(whl)-1):
		# detect jump
		if whl[i][0] < 1000 and whl[i+1][0] < 1000 and distance(whl[i], whl[i+1]) > MINJUMP:
			# see if returns to RETRAD from starting within MAXTIM
			returns = False
			for j in range(i+1, min(i+MAXTIME, len(whl))):
				if whl[j][0] < 1000 and distance(whl[j], whl[i]) < RETRAD:
					returns = True
					jumpend = j
					break

			if returns:
				print 'JUMP IS DETECTED AND REMOVED; to', whl[i+1], 'at', i
				for k in range(i+1, jumpend):
					whl[k] = whl[i][:]

	return whl

#============================================================================================================================================================================
def read_trials(path):
	tr = []
	for line in open(path):
		if len(line) < 2:
			continue
		ws = line.split(' ')
		tr.append([int(ws[0]), int(ws[1])])

	return tr

#============================================================================================================================================================================
def get_environments(whl, trials):
	envs = []
	for trial in trials:
		whli= trial[0] / WHLRES
		while whl[whli] < 0:
			whli += 1
		envs.append(int(whl[whli][0] < EBORD))
	return np.array(envs)

#============================================================================================================================================================================
# returns (path_length, smoothed whl, time goal reached - from start of the session)
def path_length_reach(whl, speed, speed_thold, frm, to, gx, gy, end):
	fig, (ax1, ax2) = plt.subplots(1,2, figsize=(20,10))
	ax1.plot([w[0] for w in whlo[frm:to]], [w[1] for w in whlo[frm:to]])
	ax1.plot([w[0] for w in whlo[to:end]], [w[1] for w in whlo[to:end]], color='grey')

        #whls = smooth_whl(whl)
	# smoothed before already
	whls = whl

	# DEBUG
	ax2.plot([w[0] for w in whls[frm:to]], [w[1] for w in whls[frm:to]])
	ax2.plot([w[0] for w in whls[to:end]], [w[1] for w in whls[to:end]], color='grey')
	ax2.scatter([gx], [gy], s=100, color='green')
	plt.show()

        pl = 0
        for i in range(frm, to):
                #if speed[i] > speed_thold:
                d = distance(whls[i+1], whls[i])
                if whls[i+1][0] > 0 and whls[i][0] > 0: #and d < 25:
                	pl += d

                #if whls[i+1][0] > 0 and whls[i][0] > 0 and d > 25:
		#	print 'Ignore jump'

                # !!! WHAT IF NOT PICKED !!! - NO REACH CHECK, CALCULATE A PATH ON WHAT IS GIVEN !!!
                #dg = distance(whls[i+1], [gx, gy])
                #if dg < 5: # ???
                #       return pl, whls, i

        return pl


#============================================================================================================================================================================
# last timepoint when the animal ws withing the given radius of the goal
# 	=> after that went straight to the SB
def time_reached_backtrack(whl, first1start, first1end, gx1, gy1):
	for i in reversed(range(first1start, first1end)):
		if distance(whl[i], [gx1, gy1]) < REACHRAD:
			break

	if i == first1end:
		print 'WARNING: NO GOAL REACH DETECTED IN LEARNING / ENV 1, set time to -1 !!!'
		time_reached = -1
	else:
		time_reached = i

	return time_reached

#============================================================================================================================================================================
def time_reached(whl, speed, first1start, first1end, gx1, gy1):
	ingoal = False
	ingoal_start = 0

	print 'Look for goal %d, %d reach between %d and %d' % (gx1, gy1, first1start, first1end)

	reach_early = [-1]
	LAST_EARLY = -1

	for i in range(first1start, first1end):
		if distance(whl[i], [gx1, gy1]) < REACHRAD:
			if first1end - i > MAXBACK:
				# for logging
				if i - reach_early[-1] > 100:
					reach_early.append(i)
					LAST_EARLY = i
				continue
	
			if ingoal:
				if i - ingoal_start > INGOAL_MIN:
					break
			else:
				ingoal = True
				ingoal_start = i
		else:
			ingoal = False

	time_reached_1_l = i

	if i == first1end - 1:
		# better early reach than no reach
		if LAST_EARLY > 0:
			print 'EARLY reach counted'
			time_reached_1_l = LAST_EARLY
		else:
			print 'WARNING: NO GOAL REACH DETECTED IN LEARNING / ENV 1, set time to -1 !!!' # trial duration'
			print '   between %d and %d' % (first1start, first1end)
			#time_to_reach1_l = first1end - first1start
			time_reached_1_l = -1

	if len(reach_early) > 1:
		print 'EARLY REACH HAPPENED ON', reach_early[1:]

	return time_reached_1_l

#============================================================================================================================================================================
def get_lengthes(whl, trials, goals, sbs):
	print 'WARNING: whl smoothed before legnth calculation'

	# DEBUG
	#fig, (ax1, ax2) = plt.subplots(1,2, figsize=(20,10))
        #ax1.plot([w[0] for w in whl], [w[1] for w in whl])
	whl = filter_jumps(whl) 
	whlo = whl[:]
        # ax2.plot([w[0] for w in whl], [w[1] for w in whl])
	whl = smooth_whl(whl)
        #ax2.plot([w[0] for w in whl], [w[1] for w in whl])
	#plt.show()

	#whl = filter_jumps(whl) 
	#whl = smooth_whl(whl)

	ls = []
	for i, trial in enumerate(trials):
		if i < SKIP:
			continue

		whlis = trial[0] / WHLRES
		whlie = trial[1] / WHLRES

		# ??? FIND FIRST VALID?
		env = int(whl[whlis][0] > EBORD)

		# shortest path - from starting point to corresponding goal	
		while whl[whlis][0] < 0.1:
			whlis += 1

		# minimal possible distance - from first valid position to the goal
		MINDIST = float(distance(whl[whlis], goals[env]))
		# print goals[env], sbs[env]

		# ! OVERRIDE WITH SB DISTANCE !
		MINDISTSB = distance(goals[env], sbs[env])
		#MINDIST = MINDISTSB

		print '%d-th trial min distance: %.2f' % (i, MINDIST)

		if MINDIST < MINDISTSB / 3:
			#print 'WARNING: MINDIST too small, replace with a distance from startbox to goal =', MINDISTSB
			#MINDIST = MINDISTSB
			print 'WARNING: MINDIS too small, set TR to -1'
			tr = -1
			# ALL PATH
			# ls.append(path_length(whl[whlis:whlie]))
		else:
			tr = time_reached(whl, speed, whlis, whlie, goals[env][0], goals[env][1])
			#tr = time_reached_backtrack(whl, whlis, whlie, goals[env][0], goals[env][1])

		#pl = path_length(whl[whlis:whlie])
		if tr > 0:
			pl = path_length_reach(whl, speed, SPEED_THOLD, whlis, tr, goals[env][0], goals[env][1], whlie)
		else:
			pl = -1
			# DEBUG
			plt.plot([w[0] for w in whl[whlis:whlie]], [w[1] for w in whl[whlis:whlie]])
			plt.show()

		print 'PATH LENGTH =', pl

		if MEAS == 'APN':
			# ALL PATH - NORMALIZED
			ls.append(pl / float(MINDIST))
		elif MEAS == 'EP':
			# EXCESS PATH
			ls.append(pl - MINDIST)

	return np.array(ls)
#============================================================================================================================================================================
def read_whl_short(path):
	whl = []
	for line in open(path):
		ws = line.split(' ')
		whl.append([float(ws[0]), float(ws[1])])
	return whl
#============================================================================================================================================================================
print 'WARNING: whl to res ratio of 480 assumed'

if len(argv) < 4:
	print 'USAGE: (1)<whl file 1> (2)<trials file 1> (3)<measure> (4-OPTIONAL)<wl file 2> (5-OPTIONAL)<trials file 2> '
	print '		measures: APN = all path normalized; EP = excess path'
	print 'PLOT LEARNING CURVES, two sets will be merged if provided'
	exit(0)

argv = resolve_vars(argv + ['%{day}'], True)
DAY = argv[-1]
argv = argv[:-1]

WHLRES = 480
EBORD = 200
REACHRAD = 10
INGOAL_MIN = 25
SPEED_THOLD = 4
MAXBACK = 1500 # 30 seconds / was 1500 !!!

# DAY SPECIFIC
if DAY == '0109':
	MAXBACK = 1000
	print MAXBACK, 'MAXBACK for 0109'

if DAY == '0226':
	MAXBACK = 500
	#INGOAL_MIN=10
	print MAXBACK, 'MAXBACK for 0226'

if DAY == '0428':
	MAXBACK = 500 # or 500 / 1500
	#REAHRAD = 3
	print MAXBACK, 'MAXBACK for 0428'

if DAY == '0503':
	MAXBACK = 500
	print MAXBACK, 'MAXBACK for 0503'

TWO = (len(argv) > 4) and (argv[4] != '-t')
print TWO

if len(argv)>4 and argv[-2] == '-t':
	SKIP = int(argv[-1])
else:
	SKIP = 0

# find out the format
line = open(argv[1]).readline().split(' ')
SHORT = len(line) <= 2

REPLUNK = True

whl = read_whl_short(argv[1]) if SHORT else  whl_to_pos(open(argv[1]), REPLUNK)
trials = read_trials(argv[2])

MEAS = argv[3]
if MEAS not in ['APN', 'EP']:
	print 'Valid measrues are APN and EP'
	exit(1)

[g1x, g1y, g2x, g2y, sb1x, sb1y, sb2x, sb2y] = [float(c) for c in resolve_vars(['%{g1x}', '%{g1y}', '%{g2x}', '%{g2y}', '%{sb1x}', '%{sb1y}', '%{sb2x}', '%{sb2y}'], True)]
# find shortest distance to the goal : from starting point to the goal cordinates
goals = [[g1x, g1y], [g2x, g2y]]
sbs = [[sb1x, sb1y], [sb2x, sb2y]]

# original, not smoothed
whlo = whl[:]

speed = whl_to_speed(whl)
lengthes = get_lengthes(whl, trials, goals, sbs)
envs = get_environments(whl, trials)

whlpath2 = argv[4] if TWO else ''
trialspath2 = argv[5] if TWO else ''

if TWO:
	whl2 = read_whl_short(whlpath2) if SHORT else whl_to_pos(open(whlpath2), REPLUNK)
	trials2 = read_trials(trialspath2)
	lengthes2 = get_lengthes(whl2, trials2, goals, sbs)
	envs2 = get_environments(whl2, trials2)

	# FOR 9F+9L - MERGE THE TWO
	lengthes = np.append(lengthes, lengthes2)
	envs = np.append(envs, envs2)

DISPLAY = False

if DISPLAY:
	lw = 5
	plt.figure()
	plt.plot(lengthes[envs == 0], linewidth = lw)
	plt.plot(lengthes[envs == 1], linewidth = lw, color='r')
	#if TWO:
	#	plt.plot(lengthes2, color = 'red', linewidth = lw)
	plt.grid()
	plt.show()

# save
outpath = (whlpath2 if TWO else argv[1]) + '.learning.rev5'
if os.path.isfile(outpath):
	print 'ERROR: output file exists'
	exit(1)

foutpath = open(outpath, 'w')
foutpath.write('%d\n' % np.sum(envs == 0))
for ln in lengthes[envs == 0]:
	foutpath.write('%f\n' % ln)
foutpath.write('%d\n' % np.sum(envs == 1))
for ln in lengthes[envs == 1]:
	foutpath.write('%f\n' % ln)
