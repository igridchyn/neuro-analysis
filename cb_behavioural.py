#!/usr/bin/env python

from sys import argv
from tracking_processing import *
import os 
from matplotlib import pyplot as plt
import numpy as np
from call_log import *

	
# assumes input times are alredy from start to goal !
# JUST CALCULATES PATH LENGTH
# returns (path_length, smoothed whl, time goal reached - from start of the session)
def path_length_reach(whl, speed, speed_thold, frm, to, gx, gy):
	whls = smooth_whl(whl)

	pl = 0
	for i in range(frm, to):
		#if speed[i] > speed_thold:
		d = distance(whls[i+1], whls[i])
		if whls[i+1][0] > 0 and whls[i][0] > 0 and d < 40:
			pl += d

		# !!! WHAT IF NOT PICKED !!! - NO REACH CHECK, CALCULATE A PATH ON WHAT IS GIVEN !!!
		#dg = distance(whls[i+1], [gx, gy])
		#if dg < 5: # ???
		#	return pl, whls, i

	return pl, whls, i

def goal_dists(whl, goal, frm, to):
	gdists = []
	for i in range(frm, to):
		if whl[i][0] > 0.1:
			gdists.append(distance(goal, whl[i]))

	return gdists

def goal_dists_speed(whl, goal, frm, to, speed, speed_thold):
	gdists = []
	for i in range(frm, to):
		if speed_thold > 0 and speed[i] > speed_thold:
			gdists.append(distance(goal, whl[i]))
		if speed_thold < 0 and speed[i] < abs(speed_thold):
			gdists.append(distance(goal, whl[i]))

	return gdists

# number of entries
def number_of_crossings(whl, frm, to, goal, radius):
	out = True
	ncross = 0
	tin = 0
	for i in range(frm, to):
		if out:
			if distance(goal, whl[i]) < radius:
				out = False
				tin = i
				# ncross += 1
		else:
			if distance(goal, whl[i]) > radius:
				out = True
				if i - tin > INTHOLD:
					ncross += 1

	return ncross

def scale_pos(pos, scales):
	if pos[0] == 0:
		return [0, 0]
	BORDERX = 200
	if pos[0] < BORDERX:
		return [pos[0] / scales[0], pos[1] / scales[0]]
	else:
		return [(pos[0] - BORDERX) / scales[1] + BORDERX, pos[1] / scales[1]]

def scale_whl(whl, scales):
	whls = []
	for pos in whl:
		whls.append(scale_pos(pos, scales))			
	return whls
	
#==========================================================================================================================================================================================
if len(argv) < 2:
	print 'Usage: (1)< 0/1 : whether results should be plotted (or only written to an output file)>'
	exit(0)

plot = bool(int(argv[1]))
logdir = log_call(argv)
# for tracking processing
# log_call(['/home/igor/bin/source/tracking_processing.py'])

# CONSTANTS
cdesc1 ='max distance considered for the goal distance histogram'
DMAX = 50
cdesc2 = 'speed threshold - for moving time in the first trial and time spend moving around the goal in the post-probe'
SPEED_THOLD = 4
cdesc3 = 'min time to spend within the goal in the computation of time to reach the goal'
INGOAL_MIN = 50 # 10, 0 for NEW-LEARNING
cdesc4 = 'min time to be withing the goal radius in the number of crossings calculation'
INTHOLD = 50 # 50 for R=100; 25 for R=5
cdesc5= 'Radius to reach the goal and stay inside'
REACHRAD = 10 # 5, 10 - works for updated time/length calculation method / actually not - was buggy

print 'The following parameters are used in the calculations: %s = %d\n\t%s = %d\n\t%s = %d\n\t%s = %d\n\t%s=%d' % (cdesc1, DMAX, cdesc2, SPEED_THOLD, cdesc3, INGOAL_MIN, cdesc4, INTHOLD, cdesc5, REACHRAD)

#whlpath=argv[1]
#whlpathpost = argv[2]

animal = ''
date = ''
postp_ses = ''
postl_ses = ''
estart = ''
# scales = [0.87, 0.971]
scales = [1.0, 1.0]

# READ SWAP FROM ABOUT TXT
#fab = open('about.txt')
fab = open('about_old.txt')

for line in fab:
	ws = line.split(' ')

	if len(ws) < 2:
		continue
	if ws[-1][-1] == '\n':
		ws[-1]= ws[-1][:-1]

	if ws[0] == 'swap':
		swap = bool(int(ws[1]))
	if ws[0] == 'animal':
		animal = ws[1]
	if ws[0] == 'pps':
		postp_ses = ws[1]
	if ws[0] == 'pls':
		postl_ses = ws[1]
	if ws[0] == 'date':
		date = ws[1]
	if ws[0] == 'estart':
		estart = int(ws[1])

	try:
		fval = float(ws[1])
		if ws[0] == 'sb1x':
			sb1x = fval
		if ws[0] == 'sb1y':
			sb1y = fval
		if ws[0] == 'sb2x':
			sb2x = fval
		if ws[0] == 'sb2y':
			sb2y = fval
		if ws[0] == 'g1x':
			gx1 = fval
		if ws[0] == 'g1y':
			gy1 = fval
		if ws[0] == 'g2x':
			gx2 = fval
		if ws[0] == 'g2y':
			gy2 = fval
	except:
		pass

if estart == 1:
	scales = [scales[1], scales[0]]

# scale goals and sb coords
# !!! ALREADY SCALED IN THE NEW ABOUT.TXT !!!
#[gx1, gy1] = scale_pos([gx1, gy1], scales)
#[gx2, gy2] = scale_pos([gx2, gy2], scales)
#[sb1x, sb1y] = scale_pos([sb1x, sb1y], scales)
#[sb2x, sb2y] = scale_pos([sb2x, sb2y], scales)

whlpath = postl_ses + '/' + animal + '_' + date[2:] + '_' + postl_ses + '.whl'
whlpathpost = postp_ses + '/' + animal + '_' + date[2:] + '_' + postp_ses + '.whl'

if len(animal) == 0 or len(postp_ses) == 0 or len(postl_ses) == 0 or  len(date) == 0:
	print 'One of the following parameters is missing from the about.txt: pls/pps/animal/swap/date'
	exit(1)

log_file(logdir, 'about.txt')

base = whlpath.split('/')[-1].split('.')[0]
# ========= POST-LEARNING ANALYSES ======================

# open output and read first trials in every environment
ftr = open(whlpath + '.trials')

trials = []
for line in ftr:
	if len(line) < 2:
		continue
	ws = line.split(' ')
	trials.append([int(ws[0]), int(ws[1])])
print 'Trials read: ', trials

whl = whl_to_pos(open(whlpath), True)
#whl = scale_whl(whl, scales)

print 'WARNING: assuming first trials in environments 1/2 to be trials number 1 and 6 correspondingly !'

ft2 = 5
if '0106' in whlpath:
	ft2 = 1
if '1129' in whlpath:
	ft2 = 3
if '1123' in whlpath:
	ft2 = 10

first1start = trials[0][0] / 480
first1end = trials[0][1] / 480
first2start = trials[ft2][0] / 480
first2end = trials[ft2][1] / 480

#i=0
#SEPX = 200
#while whl[i][0] < SEPX or whl[i][0] > 1000 or whl[i][0] < 0.1:
#	i += 1
#first1end = i
#while whl[i][0] >= SEPX or whl[i][0] > 1000 or whl[i][0] < 0.1:
#	i += 1
#first2end = i

# 1. Trial time
first1time = first1end - first1start
first2time = first2end - first2start
print 'First trial times: %d / %d' % (first1time, first2time)

# 2. Moving time
speed = whl_to_speed(whl)

# DEBUG
# spa = np.array(speed)
# plt.hist(spa[spa < 15], 50)
# plt.show()

move1 = 0
# !!! SEE SPEED DISTRIBUTION !!!
for i in range(first1start, first1end):
	if speed[i] > SPEED_THOLD:
		move1 += 1

move2 = 0
for i in range(first2start, first2end):
	if speed[i] > SPEED_THOLD:
		move2 += 1










# COPY FROM POST
# TODO: box time after post sep ?
# 4. TIME AND DISTANCE OF REACHING THE GOAL - LEARNING
ingoal = False
ingoal_start = 0

print 'Look for goal 1 reach between %d and %d' % (first1start, first1end)

for i in range(first1start, first1end):
	if distance(whl[i], [gx1, gy1]) < REACHRAD:
		if ingoal:
			if i - ingoal_start > INGOAL_MIN:
				
				# count moving points withing post1out to i
				ttr = 0
				for j in range(first1start, i):
					if whl[j][0] > 0.1 and whl[j][0] < 1000 and speed[j] > SPEED_THOLD:
						ttr += 1

				#time_to_reach1 = i - post1out
				time_to_reach1_l = ttr
				break
		else:
			ingoal = True
			ingoal_start = i
	else:
		ingoal = False

time_reached_1_l = i

if i == first1end - 1:
	print 'WARNING: NO GOAL REACH DETECTED IN LEARNING / ENV 1, set time to trial duration'
	time_to_reach1_l = first1end - first1start

ingoal = False
print 'Look for goal 2 reach between %d and %d' % (first2start, first2end)
for i in range(first2start, first2end):
	if distance(whl[i], [gx2, gy2]) < REACHRAD:
		if ingoal:
			if i - ingoal_start > INGOAL_MIN:
				ttr = 0
				for j in range(first2start, i):
					if whl[j][0] > 0.1 and whl[j][0] < 1000 and speed[j] > SPEED_THOLD:
						ttr += 1

				time_to_reach2_l = ttr #i - post2out
				break
		else:
			ingoal = True
			ingoal_start = i
	else:
		ingoal = False

if i == first2end - 1:
	print 'WARNING: NO GOAL REACH DETECTED IN LEARNING / ENV 2, set trial duration'
	time_to_reach2_l = first2end - first2start

time_reached_2_l = i

# overrides old calculations below
pl1, whls, treach1 = path_length_reach(whl, speed, SPEED_THOLD, first1start, time_reached_1_l, gx1, gy1)
pl2, whls, treach2 = path_length_reach(whl, speed, SPEED_THOLD, first2start, time_reached_2_l, gx2, gy2)
searchtime1 = time_to_reach1_l
searchtime2 = time_to_reach2_l




















# 3. Path length 0 overriden by the above
#pl1, whls, treach1 = path_length_reach(whl, speed, SPEED_THOLD, first1start,  first1end, gx1, gy1)
#pl2, whls, treach2 = path_length_reach(whl, speed, SPEED_THOLD, first2start,  first2end, gx2, gy2)
#searchtime1 = treach1 - first1start
#searchtime2 = treach2 - first2start

# FIND THE FIRST VALID POINT SINCE first1start and first2start and normalize on difference from those to the goal == optimal path
i = first1start
while whl[i][0] < 0.1:
	i += 1
fv1 = whl[i]
i = first2start
while whl[i][0] < 0.1:
	i += 1
fv2 = whl[i]

print 'WARNING: ABSOLUTE EXCESS PATH, NOT NORMALIZED BY MINIMAL PATH LENGTH, ONLY SUBRACTED'
#pl1 -= sqrt((sb1x - gx1) ** 2 + (sb1y - gy1) ** 2)
#pl2 -= sqrt((sb2x - gx2) ** 2 + (sb2y - gy2) ** 2)
pl1 /= sqrt((fv1[0] - gx1) ** 2 + (fv1[1] - gy1) ** 2)
pl2 /= sqrt((fv2[0] - gx2) ** 2 + (fv2[1] - gy2) ** 2)

# scale time to reach the goal similarly
searchtime1 /= sqrt((sb1x - gx1) ** 2 + (sb1y - gy1) ** 2)
searchtime2 /= sqrt((sb2x - gx2) ** 2 + (sb2y - gy2) ** 2)

# ========= POST-PROBE ANALYSES ======================
whlp = whl_to_pos(open(whlpathpost), True)
# whlp = smooth_whl(whlp)
whlp = scale_whl(whlp, scales)

speedp = whl_to_speed(whlp)
# Find separation of posts - by DX coord
i=0
SEPX = 200
while whlp[i][0] < SEPX or whlp[i][0] > 1000 or whlp[i][0] < 0.1:
        i += 1
postsep = i

print 'postsep = %s, whlp length = %d' % (postsep, len(whlp))

# 1. Time spent within goals - histograms
gdists1 = goal_dists(whlp, [gx1, gy1], 0, postsep)
gdists2 = goal_dists(whlp, [gx2, gy2], postsep, len(whlp))

sbdists1 = np.array(goal_dists(whlp, [sb1x, sb1y], 0, postsep))
sbdists2 = np.array(goal_dists(whlp, [sb2x, sb2y], postsep, len(whlp)))

#gdists1 = [g for g in gdists1 if g < DMAX]
#gdists2 = [g for g in gdists2 if g < DMAX]
gdists1 = np.array(gdists1)
gdists2 = np.array(gdists2)
#gdists1 = gdists1[sbdists1 > 50]
#gdists2 = gdists2[sbdists2 > 50]

print 'hists of goals dists:'
print np.histogram(gdists1, [0, 10, 30, 40, 50, 60])
print np.histogram(gdists2, [0, 10, 30, 40, 50, 60])

# 2. Number of crossings - for different radius values : 10/20/30
ncross1 = []
ncross2 = []
for radius in [10, 20, 30]:
	ncross1.append(number_of_crossings(whlp, 0, postsep, [gx1, gy1], radius))
	ncross2.append(number_of_crossings(whlp, postsep, len(whlp), [gx2, gy2], radius))

# 3. Time spent running withing goals
gdists1s = goal_dists_speed(whlp, [gx1, gy1], 0, postsep, speedp, SPEED_THOLD)
gdists2s = goal_dists_speed(whlp, [gx2, gy2], postsep, len(whlp), speedp, SPEED_THOLD)
# gdists1s = [g for g in gdists1s if g < DMAX]
# gdists2s = [g for g in gdists2s if g < DMAX]

gdists1ls = goal_dists_speed(whlp, [gx1, gy1], 0, postsep, speedp, -SPEED_THOLD)
gdists2ls = goal_dists_speed(whlp, [gx2, gy2], postsep, len(whlp), speedp, -SPEED_THOLD)

# output to file
dbins = [i*10 for i in range(300)]
nrmd = False # True
dhist1, bdhist1 = np.histogram(gdists1, dbins, normed = nrmd)
dhist2, bdhist2 = np.histogram(gdists2, dbins, normed = nrmd)
dhist1 = dhist1.astype(float) / np.sum(dhist1)
dhist2 = dhist2.astype(float) / np.sum(dhist2)

dhist1s, b = np.histogram(gdists1s, dbins, normed = nrmd)
dhist2s, b = np.histogram(gdists2s, dbins, normed = nrmd)
dhist1s = dhist1s.astype(float) / np.sum(dhist1s)
dhist2s = dhist2s.astype(float) / np.sum(dhist2s)
dhist1ls, b = np.histogram(gdists1ls, dbins, normed = nrmd)
dhist2ls, b = np.histogram(gdists2ls, dbins, normed = nrmd)
dhist1ls = dhist1ls.astype(float) / np.sum(dhist1ls)
dhist2ls = dhist2ls.astype(float) / np.sum(dhist2ls)

SBLEAVERAD=10 # 30

# TODO: box time after post sep ?
# 4. Time to reach the goal - POST
for i in range(0, postsep):
	if whlp[i][0] < 0.1 or whlp[i][0] > 1000:
		continue
	if distance(whlp[i], [sb1x, sb1y]) > SBLEAVERAD:
		post1out = i
		break

ingoal = False
ingoal_start = 0

for i in range(post1out, postsep):
	if distance(whlp[i], [gx1, gy1]) < REACHRAD:
		if ingoal:
			if i - ingoal_start > INGOAL_MIN:
				
				# count moving points withing post1out to i
				ttr = 0
				for j in range(post1out, i):					
					if whlp[j][0] > 0.1 and whlp[j][0] < 1000 and speedp[j] > SPEED_THOLD:
						ttr += 1

				#time_to_reach1 = i - post1out
				time_to_reach1 = ttr
				break
		else:
			ingoal = True
			ingoal_start = i
	else:
		ingoal = False

time_reached_1 = i

if i == postsep - 1:
	print 'WARNING: NO GOAL REACH DETECTED IN ENV 1 (POST), set time to trial duration'
	time_to_reach1 = postsep - post1out	

for i in range(postsep + 10, len(whlp)):
	if whlp[i][0] < 0.1 or whlp[i][0] > 1000:
		continue
	if distance(whlp[i], [sb2x, sb2y]) > SBLEAVERAD:
		post2out = i
		break

ingoal = False
for i in range(post2out, len(whlp)):
	if distance(whlp[i], [gx2, gy2]) < REACHRAD:
		if ingoal:
			if i - ingoal_start > INGOAL_MIN:
				ttr = 0
				for j in range(post2out, i):					
					if whlp[j][0] > 0.1 and whlp[j][0] < 1000 and speedp[j] > SPEED_THOLD:
						ttr += 1

				time_to_reach2 = ttr #i - post2out
				break
		else:
			ingoal = True
			ingoal_start = i
	else:
		ingoal = False

if i == len(whlp) - 1:
	print 'WARNING: NO GOAL REACH DETECTED IN ENV 2 (POST), set trial duration'
	time_to_reach2 = len(whlp) - post2out

time_reached_2 = i

pl1p, whlsp, treach1p = path_length_reach(whlp, speedp, SPEED_THOLD, post1out, time_reached_1, gx1, gy1)
pl2p, whlsp, treach2p = path_length_reach(whlp, speedp, SPEED_THOLD, post2out, time_reached_2, gx2, gy2)
# normalize by distance to the goal
pl1p /= sqrt((sb1x - gx1) ** 2 + (sb1y - gy1) ** 2)
pl2p /= sqrt((sb2x - gx2) ** 2 + (sb2y - gy2) ** 2)

# ========= PLOTTING ======================
# 3 X 2
if (plot):
	barx_nc = np.array(range(len(ncross1)))
	barx = np.array([0, 1])
	f, ((ax0, ax1, ax2), (ax3, ax4, ax5), (ax6, ax7, ax8)) = plt.subplots(3, 3, figsize=(20, 10))
	bl=ax0.bar(barx, [first1time, first2time], width = 0.2)
	bl[1].set_color('r')
	ax0.set_title('First trial times')
	bl=ax1.bar(barx, [move1, move2], width = 0.2)
	bl[1].set_color('r')
	ax1.set_title('First trial moving times')
	bl=ax2.bar(barx, [pl1, pl2], width = 0.2)
	bl[1].set_color('r')
	ax2.set_title('First trial path lengthes')
	#ax3.hist(np.array(gdists1), [i*5 for i in range(0,100)], alpha=0.5, normed=True)
	#ax3.hist(np.array(gdists2), [i*5 for i in range(0,100)], alpha=0.5, color='r', normed=True)
	ax3.bar(bdhist1[:-1], dhist1, alpha=0.5)
	ax3.bar(bdhist2[:-1], dhist2, alpha=0.5, color='r')
	ax3.set_title('Post time spent within goals')
	ax4.bar(barx_nc, ncross1, width=0.2)
	ax4.bar(barx_nc + 0.2, ncross2, width=0.2, color='r')
	ax4.set_title('Number of crossings')
	ax5.hist(np.array(gdists1s), [i*5 for i in range(0,10)], alpha=0.5, normed=True)
	ax5.hist(np.array(gdists2s), [i*5 for i in range(0,10)], alpha=0.5, color='r', normed=True)
	ax5.set_title('Post time spent running within goals, ST=%.1f' % SPEED_THOLD)
	f.suptitle(whlpath.split('.')[0].replace('_', ' '), fontsize=20)
	bl=ax6.bar(barx, [time_to_reach1, time_to_reach2], width=0.2)
	ax6.set_title('Time to reach goal (10 cm radius)')
	bl[1].set_color('r')

	ax7.plot([p[0] for p in whls[first1start:first1end]], [p[1] for p in whls[first1start:first1end]])
	ax7.plot([p[0] for p in whls[first2start:first2end]], [p[1] for p in whls[first2start:first2end]], color='r')
	# until goal reach
	#ax7.plot([p[0] for p in whlp[:time_reached_1]], [p[1] for p in whlp[:time_reached_1]])
	#ax7.plot([p[0] for p in whlp[postsep:time_reached_2]], [p[1] for p in whlp[postsep:time_reached_2]], color = 'r')
	ax7.scatter(gx1, gy1, s=30, color='red')
	ax7.scatter(gx2, gy2, s=30)
	ax7.scatter(sb1x, sb1y, s=30, color = 'green')
	ax7.scatter(sb2x, sb2y, s=30, color = 'green')
	ax7.set_title('Post until goal reached')

	ax8.hist(np.array(gdists1ls), [i*5 for i in range(0,10)], alpha=0.5, normed=True)
        ax8.hist(np.array(gdists2ls), [i*5 for i in range(0,10)], alpha=0.5, color='r', normed=True)
	ax8.set_title('Post time spent withing goals, SPEEDM<%.2f' % SPEED_THOLD)

	f.savefig(logdir + 'CB_BEH' + base + '.png')

	plt.show()

print 'FTPL:', pl1, pl2
print 'D10: ', dhist1[0], dhist2[0]
print 'NC10:', ncross1[0], ncross2[0]

#print 'WARNING: NO DUMP, TEST RUN'
outpath = whlpath + '.cbbeh.revtest'
if os.path.isfile(outpath):
	print 'ERROR: output file exists!'
	exit(1)

fout = open(outpath, 'w')
if swap:
	fout.write('d10 %f %f\n' % (dhist1[0], dhist2[0]))
	fout.write('d10_s %f %f\n' % (dhist1s[0], dhist2s[0]))
	fout.write('d10_ls %f %f\n' % (dhist1ls[0], dhist2ls[0]))
	fout.write('trg %f %f\n' % (time_to_reach1, time_to_reach2))
	fout.write('trgl %f %f\n' % (searchtime1, searchtime2))
	fout.write('nc10 %f %f\n' % (ncross1[0], ncross2[0]))
	fout.write('ftpl %f %f\n' % (pl1, pl2))
	fout.write('prg %f %f\n' % (pl1p, pl2p))
else:
	fout.write('d10 %f %f\n' % (dhist2[0], dhist1[0]))
	fout.write('d10_s %f %f\n' % (dhist2s[0], dhist1s[0]))
	fout.write('d10_ls %f %f\n' % (dhist2ls[0], dhist1ls[0]))
	fout.write('trg %f %f\n' % (time_to_reach2, time_to_reach1))
	fout.write('trgl %f %f\n' % (searchtime2, searchtime1))
	fout.write('nc10 %f %f\n' % (ncross2[0], ncross1[0]))
	fout.write('ftpl %f %f\n' % (pl2, pl1))
	fout.write('prg %f %f\n' % (pl2p, pl1p))
fout.close()
log_file(logdir, outpath)
