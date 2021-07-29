#!/usr/bin/env python

from sys import argv
from tracking_processing import *
import os 
from matplotlib import pyplot as plt
import numpy as np
from call_log import *
from iutils import *
	
# assumes input times are alredy from start to goal !
# JUST CALCULATES PATH LENGTH
# returns (path_length, smoothed whl, time goal reached - from start of the session)
def path_length_reach(whl, speed, speed_thold, frm, to, gx, gy):
	whls = smooth_whl(whl)

	pl = 0
	for i in range(frm, to):
		#if speed[i] > speed_thold:
		d = distance(whls[i+1], whls[i])
		if whls[i+1][0] > 0 and whls[i][0] > 0 and d < 10:
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

def trg(start, end, gx, gy):	
	ingoal = False
	print 'Look for goal reach between %d and %d' % (start, end)
	for i in range(start, end):
		if distance(whl[i], [gx, gy]) < REACHRAD:
			if ingoal:
				if i - ingoal_start > INGOAL_MIN:
					ttr = 0
					for j in range(start, i):
						if whl[j][0] > 0.1 and whl[j][0] < 1000 and speed[j] > SPEED_THOLD:
							ttr += 1

					#time_to_reach = ttr #i - post2out
					break
			else:
				ingoal = True
				ingoal_start = i
		else:
			ingoal = False
	# CHECK THE 2ND !
	return i, i - start


#==========================================================================================================================================================================================
if len(argv) < 11:
	print 'Usage: (1)<whl file> (2)<Base radius for number of crossings> (3)<Distance resolution for dwell time> (4)<Object reach radius> (5)<Speed threshold> (6)<whl scale> (7)<Min time to count as object reach> (8)<Min time withing object to count as crossing> (9)<Goals file> (10)<Time limit - sec>'
	exit(0)

plot = True
logdir = log_call(argv)

# DISTANCE SCALE FOR DWELL TIME
DHBASE=float(argv[3])
# RADIUSES FOR NUMBER OF CROSSINGS
NCBASE=float(argv[2])
ncrads = [NCBASE, 2*NCBASE, 3*NCBASE]
# CONSTANTS
cdesc1 ='max distance considered for the goal distance histogram'
DMAX = 50
cdesc2 = 'speed threshold - for moving time in the first trial and time spend moving around the goal in the post-probe'
SPEED_THOLD = float(argv[5])
cdesc3 = 'min time to spend within the goal in the computation of time to reach the goal'
INGOAL_MIN = int(argv[7]) # 10, 0 for NEW-LEARNING
cdesc4 = 'min time to be withing the goal radius in the number of crossings calculation'
INTHOLD = int(argv[8]) # 50 for R=100; 25 for R=5
cdesc5= 'Radius to reach the goal and stay inside'
REACHRAD = float(argv[4]) # 5, 10 - works for updated time/length calculation method / actually not - was buggy

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

WHLSCALE = float(argv[6])
#s = 200/55.0
s=2.0 * WHLSCALE# 3

fg = open(argv[9])
g = [line_to_floats(l) for l in fg]
[gx1, gy1] = [g[0][i]/s for i in range(2)]
[gx2, gy2] = [g[1][i]/s for i in range(2)]
[gx3, gy3] = [g[2][i]/s for i in range(2)]

#[gx1, gy1] = [213.64/s, 370.40/s]
#[gx2, gy2] = [212.44/s, 621.32/s]
#[gx3, gy3] = [377.08/s, 625.90/s]

# scale goals and sb coords
# !!! ALREADY SCALED IN THE NEW ABOUT.TXT !!!
#[gx1, gy1] = scale_pos([gx1, gy1], scales)
#[gx2, gy2] = scale_pos([gx2, gy2], scales)
#[sb1x, sb1y] = scale_pos([sb1x, sb1y], scales)
#[sb2x, sb2y] = scale_pos([sb2x, sb2y], scales)

#whlpath = postl_ses + '/' + animal + '_' + date[2:] + '_' + postl_ses + '.whl'
whlpath = argv[1]
whlpathpost = whlpath

base = whlpath.split('/')[-1].split('.')[0]
# ========= POST-LEARNING ANALYSES ======================

trials = []
print 'Trials read: ', trials

#whl = whl_to_pos(open(whlpath), True)
#whl = scale_whl(whl, scales)
whl = []
for line in open(whlpath):
	whl.append([f/WHLSCALE for f in line_to_floats(line)])
TMAX = min(len(whl)-1, int(float(argv[10]) * 20000/512.0))
whl = whl[:TMAX]

# full length
trials = [[0, len(whl) * 512]]

print 'WARNING: assuming first trials in environments 1/2 to be trials number 1 and 6 correspondingly !'

ft2 = 0
whlscale = 512.0
first1start = int(trials[0][0] / whlscale)
first1end = int(trials[0][1] / whlscale)

# 1. Trial time
first1time = first1end - first1start

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

# COPY FROM POST
# TODO: box time after post sep ?
# 4. TIME AND DISTANCE OF REACHING THE GOAL - LEARNING
ingoal = False
ingoal_start = 0

print 'Look for goal 1 reach between %d and %d' % (first1start, first1end)

time_reached_1_l, time_to_reach1_l = trg(first1start, first1end, gx1, gy1)
time_reached_2_l, time_to_reach2_l = trg(first1start, first1end, gx2, gy2)
time_reached_3_l, time_to_reach3_l = trg(first1start, first1end, gx3, gy3)

# overrides old calculations below
pl1, whls, treach1 = path_length_reach(whl, speed, SPEED_THOLD, first1start, time_reached_1_l, gx1, gy1)
pl2, whls, treach2 = path_length_reach(whl, speed, SPEED_THOLD, first1start, time_reached_2_l, gx2, gy2)
pl3, whls, treach3 = path_length_reach(whl, speed, SPEED_THOLD, first1start, time_reached_3_l, gx3, gy3)

# INVALID VALUES ?
searchtime1 = time_to_reach1_l
searchtime2 = time_to_reach2_l
searchtime3 = time_to_reach3_l



# TIME TO SECONDS
whltscale = 20000/512.0
time_to_reach1_l /= whltscale
time_to_reach2_l /= whltscale
time_to_reach3_l /= whltscale

















# 3. Path length 0 overriden by the above
#pl1, whls, treach1 = path_length_reach(whl, speed, SPEED_THOLD, first1start,  first1end, gx1, gy1)
#pl2, whls, treach2 = path_length_reach(whl, speed, SPEED_THOLD, first2start,  first2end, gx2, gy2)
#searchtime1 = treach1 - first1start
#searchtime2 = treach2 - first2start

# FIND THE FIRST VALID POINT SINCE first1start and first2start and normalize on difference from those to the goal == optimal path
i=0
while whl[i][0] < 0.1:
	i += 1
fv1 = whl[i]

print 'WARNING: ABSOLUTE EXCESS PATH, NOT NORMALIZED BY MINIMAL PATH LENGTH, ONLY SUBRACTED'
#pl1 -= sqrt((sb1x - gx1) ** 2 + (sb1y - gy1) ** 2)
#pl2 -= sqrt((sb2x - gx2) ** 2 + (sb2y - gy2) ** 2)
pl1 -= sqrt((fv1[0] - gx1) ** 2 + (fv1[1] - gy1) ** 2)
pl2 -= sqrt((fv1[0] - gx2) ** 2 + (fv1[1] - gy2) ** 2)
pl3 -= sqrt((fv1[0] - gx3) ** 2 + (fv1[1] - gy3) ** 2)

# scale time to reach the goal similarly
# DON'T SCALE - SAME START
#searchtime1 /= sqrt((sb1x - gx1) ** 2 + (sb1y - gy1) ** 2)
#searchtime2 /= sqrt((sb2x - gx2) ** 2 + (sb2y - gy2) ** 2)

# ========= POST-PROBE ANALYSES ======================
# SAME SESSION !
whlp = whl #whl_to_pos(open(whlpathpost), True)
# whlp = smooth_whl(whlp)
whlp = scale_whl(whlp, scales)

lwhl = len(whlp)

speedp = whl_to_speed(whlp)

# 1. Time spent within goals - histograms
gdists1 = goal_dists(whlp, [gx1, gy1], 0, lwhl)
gdists2 = goal_dists(whlp, [gx2, gy2], 0, lwhl)
gdists3 = goal_dists(whlp, [gx3, gy3], 0, lwhl)

#gdists1 = [g for g in gdists1 if g < DMAX]
#gdists2 = [g for g in gdists2 if g < DMAX]
gdists1 = np.array(gdists1)
gdists2 = np.array(gdists2)
gdists3 = np.array(gdists3)

print 'hists of goals dists:'
print np.histogram(gdists1, [0, 10, 30, 40, 50, 60])
print np.histogram(gdists2, [0, 10, 30, 40, 50, 60])
print np.histogram(gdists3, [0, 10, 30, 40, 50, 60])

# 2. Number of crossings - for different radius values : 10/20/30
ncross1 = []
ncross2 = []
ncross3 = []
for radius in ncrads:
	ncross1.append(number_of_crossings(whlp, 0, lwhl, [gx1, gy1], radius))
	ncross2.append(number_of_crossings(whlp, 0, lwhl, [gx2, gy2], radius))
	ncross3.append(number_of_crossings(whlp, 0, lwhl, [gx3, gy3], radius))

# 3. Time spent running withing goals
gdists1s = goal_dists_speed(whlp, [gx1, gy1], 0, lwhl, speedp, SPEED_THOLD)
gdists2s = goal_dists_speed(whlp, [gx2, gy2], 0, lwhl, speedp, SPEED_THOLD)
gdists3s = goal_dists_speed(whlp, [gx3, gy3], 0, lwhl, speedp, SPEED_THOLD)
# gdists1s = [g for g in gdists1s if g < DMAX]
# gdists2s = [g for g in gdists2s if g < DMAX]

gdists1ls = goal_dists_speed(whlp, [gx1, gy1], 0, lwhl, speedp, -SPEED_THOLD)
gdists2ls = goal_dists_speed(whlp, [gx2, gy2], 0, lwhl, speedp, -SPEED_THOLD)
gdists3ls = goal_dists_speed(whlp, [gx3, gy3], 0, lwhl, speedp, -SPEED_THOLD)

# output to file
dbins = [i*DHBASE for i in range(300)]
nrmd = False # True
dhist1, bdhist1 = np.histogram(gdists1, dbins, normed = nrmd)
dhist2, bdhist2 = np.histogram(gdists2, dbins, normed = nrmd)
dhist3, bdhist3 = np.histogram(gdists3, dbins, normed = nrmd)
dhist1 = dhist1.astype(float) / np.sum(dhist1)
dhist2 = dhist2.astype(float) / np.sum(dhist2)
dhist3 = dhist3.astype(float) / np.sum(dhist3)

dhist1s, bs = np.histogram(gdists1s, dbins, normed = nrmd)
dhist2s, bs = np.histogram(gdists2s, dbins, normed = nrmd)
dhist3s, bs = np.histogram(gdists3s, dbins, normed = nrmd)
dhist1s = dhist1s.astype(float) / np.sum(dhist1s)
dhist2s = dhist2s.astype(float) / np.sum(dhist2s)
dhist3s = dhist3s.astype(float) / np.sum(dhist3s)
dhist1ls, b = np.histogram(gdists1ls, dbins, normed = nrmd)
dhist2ls, b = np.histogram(gdists2ls, dbins, normed = nrmd)
dhist3ls, b = np.histogram(gdists3ls, dbins, normed = nrmd)
dhist1ls = dhist1ls.astype(float) / np.sum(dhist1ls)
dhist2ls = dhist2ls.astype(float) / np.sum(dhist2ls)
dhist3ls = dhist3ls.astype(float) / np.sum(dhist3ls)

#print 'WARNING: NO DUMP, TEST RUN'
outpath = whlpath + '.beh'
fout = open(outpath, 'w')
fout.write('Dwell time %f %f %f\n' % (dhist1[0], dhist2[0], dhist3[0]))
fout.write('Dwell time speed-filtered %f %f %f\n' % (dhist1s[0], dhist2s[0], dhist3s[0]))
fout.write('Time to reach object %f %f %f\n' % (time_to_reach1_l, time_to_reach2_l, time_to_reach3_l))
fout.write('Number of crossings %f %f %f\n' % (ncross1[0], ncross2[0], ncross3[0]))
# fout.write('prg %f %f\n' % (pl2p, pl1p))
fout.close()
log_file(logdir, outpath)

# ========= PLOTTING ======================
# 3 X 2
if (plot):
	barx_nc = np.array(range(len(ncross1)))
	barx = np.array([0, 1])

	#f, ((ax0, ax1, ax2), (ax3, ax4, ax5), (ax6, ax7, ax8)) = plt.subplots(3, 3, figsize=(20, 10))
	f, ((ax3, ax4, ax5), (ax6, ax7, ax8)) = plt.subplots(2, 3, figsize=(20, 10))

	#bl=ax0.bar(barx, [first1time, first2time], width = 0.2)
	#bl[1].set_color('r')
	#ax0.set_title('First trial times')
	#bl=ax1.bar(barx, [move1, move2], width = 0.2)
	#bl[1].set_color('r')
	#ax1.set_title('First trial moving times')

	bl=ax8.bar([1,2,3], [pl1, pl2, pl3], color=['b', 'r', 'g'], width = 0.2)
	bl[1].set_color('r')
	ax8.set_title('Path till goal reached')
	ax8.set_xticks(())

	#ax3.hist(np.array(gdists1), [i*5 for i in range(0,100)], alpha=0.5, normed=True)
	#ax3.hist(np.array(gdists2), [i*5 for i in range(0,100)], alpha=0.5, color='r', normed=True)
	
	hlim = 6
	# bdhist[:-1]
	bw = (bdhist1[1]-bdhist1[0]) / 4.0
	bshift = bw
	ax3.bar(bdhist1[:hlim], dhist1[:hlim], alpha=0.5, width=bw)
	ax3.bar(bdhist2[:hlim]+bw, dhist2[:hlim], alpha=0.5, color='r', width=bw)
	ax3.bar(bdhist3[:hlim]+2*bw, dhist3[:hlim], alpha=0.5, color='g', width=bw)
	ax3.set_title('Time spent within goals')
	ax3.set_xticks(bdhist1[:hlim] + bw*1.5)
	ax3.set_xticklabels(['%.1f-%.1f' % (bdhist1[i], bdhist1[i+1]) for i in range(hlim)], fontsize=10)

	ax4.bar(barx_nc, ncross1, width=0.2)
	ax4.bar(barx_nc + 0.2, ncross2, width=0.2, color='r')
	ax4.bar(barx_nc + 0.4, ncross3, width=0.2, color='g')
	ax4.set_title('Number of crossings')
	ax4.set_xticks(barx_nc + 0.25)
	ax4.set_xticklabels([str(r) for r in ncrads])


	#ax5.hist(np.array(gdists1s), [i*5 for i in range(0,10)], alpha=0.5, normed=True)
	#ax5.hist(np.array(gdists2s), [i*5 for i in range(0,10)], alpha=0.5, color='r', normed=True)
	ax5.bar(bs[:hlim], dhist1s[:hlim], alpha=0.5, width=bw)
	ax5.bar(bs[:hlim]+bw, dhist2s[:hlim], alpha=0.5, color='r', width=bw)
	ax5.bar(bs[:hlim]+2*bw, dhist3s[:hlim], alpha=0.5, color='g', width=bw)
	ax5.set_title('Time spent running within goals, ST=%.1f' % SPEED_THOLD)
	ax5.set_xticks(bdhist1[:hlim] + bw*1.5)
	ax5.set_xticklabels(['%.1f-%.1f' % (bdhist1[i], bdhist1[i+1]) for i in range(hlim)], fontsize=10)

	f.suptitle(whlpath.split('.')[0].replace('_', ' '), fontsize=20)

	bl=ax6.bar([1,2,3], [time_to_reach1_l, time_to_reach2_l, time_to_reach3_l], color=['b','r','g'], width=0.2)
	ax6.set_title('Time to reach goal (%d cm radius)' % REACHRAD)
	bl[1].set_color('r')
	ax6.set_xticks(())

	ax7.scatter([p[0] for p in whls[first1start:first1end]], [p[1] for p in whls[first1start:first1end]], s=0.5, color='black', alpha=0.9)
	# until goal reach
	#ax7.plot([p[0] for p in whlp[:time_reached_1]], [p[1] for p in whlp[:time_reached_1]])
	#ax7.plot([p[0] for p in whlp[postsep:time_reached_2]], [p[1] for p in whlp[postsep:time_reached_2]], color = 'r')
	ax7.scatter(gx1, gy1, s=60, color='blue')
	ax7.scatter(gx2, gy2, s=60, color = 'red')
	ax7.scatter(gx3, gy3, s=60, color='green')
	ax7.set_title('Tracking and goals')

	#ax8.hist(np.array(gdists1ls), [i*5 for i in range(0,10)], alpha=0.5, normed=True)
        #ax8.hist(np.array(gdists2ls), [i*5 for i in range(0,10)], alpha=0.5, color='r', normed=True)
	#ax8.set_title('Post time spent withing goals, SPEEDM<%.2f' % SPEED_THOLD)

	f.savefig(logdir + 'CB_BEH' + base + '.png')

	plt.show()
