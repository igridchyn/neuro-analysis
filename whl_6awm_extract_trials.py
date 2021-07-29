#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
from tracking_processing import whl_to_pos, distance
import numpy as np
from call_log import *

# read whl + arm ends -> tracking data
# detect arm end reaches
# construct transition probabilities matrix

if len(argv) < 4:
	print 'Usage (1)<whl file> (2)<arm ends> (3)<starting in center (0/1)>' 
	print 'EXTRACT TRIALS FROM 6-AWM TRACKING FILE'
	exit(0)

logdir = log_call(argv)

whl = whl_to_pos(open(argv[1]), False)
arms = [[float(a.split(' ')[0]), float(a.split(' ')[1])] for a in open(argv[2]) if len(a) > 0]

starting_center = bool(int(argv[3]))

log_and_print(logdir, 'Length of whl: %d' % len(whl))
log_and_print(logdir, 'Arm ends: ' + str(arms))

# whl : 50 Hz
# in whl samples => 20 sec
SAME_VISIT_COOLDOWN = 1000
GOAL_RAD = 20
CENTER_RAD = 11
center = [88, 80]

last_visits = [-SAME_VISIT_COOLDOWN] * len(arms)

i = 0

seq = []
delays = []
ctime = []

# when arm was first visited (order number from starting arm)
first_visit = np.zeros((len(arms), 20))
visited_in_trial = [False] * len(arms)
intrial_count = 0

last_visit = 0
ct = 0
while i < len(whl):
	for ai in range(len(arms)):
		a = arms[ai]
		d = distance(whl[i], a)
		if d < GOAL_RAD and i - last_visits[ai] > SAME_VISIT_COOLDOWN and ct > 0:
			seq.append(ai)
			delays.append(i - last_visit)
			last_visits[ai] = i
			last_visit = i
			ctime.append(ct)
			ct = 0

	dc = distance(whl[i], center)

	if dc < CENTER_RAD:
		ct += 1
			
	i += 1

print 'Visits (%d)' % len(seq), seq
print [(seq[i], delays[i], ctime[i]) for i in range(len(seq))]

trials = []
if starting_center:
	# TRIALS SEPARATION / ERROR PROBABILITY ANALYSES
	# TODO CHECK FOR SKIPPED ARMS
	visited = [False] * 6
	nvis = 0
	curseq = ''
	trial = []
	for i in range(0, len(seq)):
		s = seq[i]
		curseq += str(s) + ' '
		
		trial.append(s)

		if not visited[s]:
			visited[s] = True
			nvis += 1

			if nvis == 6:
				print curseq, delays[i+1] if i < len(delays)-1 else '-', ctime[i+1] if i < len(ctime) - 1 else '-'
				curseq = ''
				nvis = 0
				visited = [False] * 6
				trials.append(trial)
				trial = []
else:
	SA_DEL = 1000
	# IN CASE OF STARTING IN THE CENTER
	# TRIALS SEPARATION ANALYSES
	# TODO CHECK FOR SKIPPED ARMS
	visited = [False] * 6
	nvis = 1
	curseq = str(seq[0]) + ' '
	trial = [seq[0]]
	visited[seq[0]] = True
	for i in range(1, len(seq)):
		s = seq[i]
		curseq += str(s) + ' '
		trial.append(s)

		if not visited[s]:
			visited[s] = True
			nvis += 1

		if nvis == 6:
			if delays[i+1] > SA_DEL:
				print curseq, delays[i+1], ctime[i+1]
				curseq = str(s) + ' '
				nvis = 1
				visited = [False] * 6
				trials.append(trial)
				trial = [s]
			else:
				print 'MISS TRIAL END!'

		visited[s] = True

# WRITE TRIALS
ft = open(argv[1] + '.trials', 'w')
for trial in trials:
	ft.write(' '.join([str(t) for t in trial]) + '\n')
ft.close()

# transition matrix
tm = np.zeros((len(arms), len(arms)))

# don't include inter-trial transitions
# TODO - detect center time for better inter-trial detection
DEL_THOLD = 1500
CENTER_THOLD = 300
starts = []
for i in range(1, len(seq)):
	#if delays[i] < DEL_THOLD:
	# otherwise - was trial start
	if ctime[i] < CENTER_THOLD:
		tm[seq[i-1], seq[i]] += 1
		intrial_count += 1
		if not visited_in_trial[seq[i]]:
			visited_in_trial[seq[i]] = True
			first_visit[seq[i], intrial_count] += 1
	else:
		starts.append(seq[i])
		intrial_count = 0
		first_visit[seq[i], 0] += 1
		visited_in_trial = [False] * len(arms)
print tm

# normalize
for i in range(len(arms)):
	tm[i, :] /= np.sum(tm[i, :])

# TODO: starting arms, visit frequency

f, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
ax1.imshow(tm, interpolation = 'none')
ax1.set_title('Transition probabilities')
ax2.hist(seq)
ax2.grid()
ax2.set_title('Visit count')
ax3.hist(starts)
ax3.grid()
ax3.set_title('Start count')
ax4.imshow(first_visit, interpolation = 'none')
ax4.set_title('First visit')
f.suptitle(argv[1])
plt.show()
