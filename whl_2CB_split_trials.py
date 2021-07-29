#!/usr/bin/env python

import os
from sys import argv
from tracking_processing import *
from matplotlib import pyplot as plt

if len(argv) < 5:
	print('Usage: (1)<start box radius> (2)<minimal time to be outside the SB> (3)<minimal time inside the radius> (4)<0/1 : exclude first two trials> (5)<whl path> (6)<optionally - trials!>')
	print('Plotting trajectories and witing intervals when animal was far from given point at a given distance for at least given time')
	print('Leaving the radius -> trial started')
	exit(0)

adic = {}
#print('WARNING: using about_old.txt')
#for line in open('../about_old.txt'):
for line in open('about.txt'):
	if len(line) == 0:
		continue

	ws = line.split(' ')
	adic[ws[0]] = ws[1].replace('\n', '')

#whlpath = adic['animal'] + '_' + adic['date'][2:] + '_' + os.getcwd().split('/')[-1].replace('_FULL', '') + '.whl'
whlpath = argv[5]

whl = whl_to_pos(open(whlpath), False)
# short format
# whl = [[float(w.split(' ')[0]), float(w.split(' ')[1])] for w in open(argv[1]) if len(w) > 0]

# sbx = float(argv[2])
# sby = float(argv[3])
sbrad = float(argv[1])
# minimal time to be outside of the SB
mint = float(argv[2])
minti = float(argv[3])
# sbx2 = float(argv[7])
# sby2 = float(argv[8])
exclude = bool(int(argv[4]))

sbx = float(adic['sb1x'])
sby = float(adic['sb1y'])
sbx2 = float(adic['sb2x'])
sby2 = float(adic['sb2y'])

sb = [sbx, sby]
sb2 = [sbx2, sby2]
i = 0
trials = []
inside = True
tout = 0
tstart = 0
tin = 0
entry = 0
skip = 0

# EXCLUDE FIRST 2 IF exclude == True
if exclude:
	print('WARNING: assuming start in the left half')
	sep = 200
	
	# skip post 1
	while whl[i][0] < sep or whl[i][0] > 1000:
		i += 1

	# skip post 2
	while whl[i][0] > sep or whl[i][0] > 1000:
		i += 1

	print('AFTER SKIP: start with %d' %i)

	tstart = i
	skip = i
	

# observed previously
env = 0
SEP = 200

while i < len(whl):
	if whl[i][0] < 0.1 or whl[i][0] > 1000:
		i +=1
		# if last known was inside, but not reached limit yet
		if not inside and tin > 0:
			tin += 1
		continue

	if inside:
		if distance(sb, whl[i]) > sbrad and distance(sb2, whl[i]) > sbrad:
			inside = False
			tstart = i
			tin = 0
	else:
		if distance(sb, whl[i]) < sbrad or distance(sb2, whl[i]) < sbrad:
			if tin == 0:
				entry = i	
			
			tin += 1

			# also consider environment switch
			#if (tin > minti) or (env==0 and distance(sb2, whl[i]) < sbrad) or (env==1 and distance(sb, whl[i]) < sbrad):
			if (tin > minti) or (env==0 and whl[i][0] > SEP) or (env==1 and whl[i][0] < SEP):
				inside = True

				if i - tstart >= mint:
					trials.append([tstart, entry])
		else:
			tin = 0

	env = 0 if whl[i][0] < SEP else 1
	i += 1

print(trials)

if trials[-1][0] != tstart:
	trials.append([tstart, len(whl) - 1])

WHL_SR = 480

if len(argv) > 6:
	print('WARNING: LOAD TRIALS!')
	ta = np.loadtxt(argv[6], dtype=int)
	trials = [ [ta[i,0] // WHL_SR, ta[i,1] // WHL_SR ] for i in range(len(ta))]
	print(trials)

px = 3
py = 5
f, axarr = plt.subplots(px, py)

i = 0
sub = 0
ptrial = [0, 1 if skip == 0 else skip]
for trial in trials:
	btrial = [ptrial[1], trial[0]]
	axarr[i % px, (i - sub) // px].plot([w[0] for w in whl[trial[0]:trial[1]] if w[0] > 0 and w[1] > 0 and w[0]<1000], [w[1] for w in whl[trial[0]:trial[1]] if w[1] > 0 and w[0] > 0 and w[0]<1000])
	axarr[i % px, (i - sub) // px].plot([w[0] for w in whl[btrial[0]:btrial[1]] if w[0] > 0 and w[1] > 0 and w[0] < 1000], [w[1] for w in whl[btrial[0]:btrial[1]] if w[1] > 0 and w[0] > 0 and w[0]<1000], color = 'r')
	axarr[i % px, (i - sub) // px].title.set_text(str(trial[0] * WHL_SR) + ' ' + str(trial[1] * WHL_SR))

	axarr[i % px, (i - sub) // px].scatter([sbx,sbx2], [sby,sby2], s=50, color='green')

	i += 1
	if i >= px * py + sub:
		print('WARNING: not all trials shown!')
		plt.suptitle(argv[1])
		plt.show()
		f, axarr = plt.subplots(px, py)
		sub += py * px

	ptrial = trial
		
plt.suptitle(argv[1])
plt.show()

#
#print('WARINING: INCLUDING SB IN TRIAL INTERVAL')
#for i in range(1, len(trials)):
#	trials[i][0] = trials[i-1][1]

# write to file
# fo = open(argv[1] + '.trials', 'w')
fo = open(whlpath + '.trials', 'w')
for trial in trials:
	fo.write('%d %d\n' % (trial[0] * WHL_SR, trial[1] * WHL_SR))
