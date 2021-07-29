#!/usr/bin/env python

from tracking_processing import *
from sys import argv
from matplotlib import pyplot as plt
from iutils import *
from call_log import *
from math import pi as PI
from math import *

def plot_by_envs(ax, xs, ys, col='grey'):
	i=0
	while xs[i] < 200:
		i+=1
	LW = 5
	ax.plot(np.array(xs[:i]), ys[:i], color=col, linewidth=LW)
	ax.plot(np.array(xs[i:])-E2SH, np.array(ys[i:])-E2SHY, color=col, linewidth=LW)

def rem_whl_art(whl):
	

	JMAX = 50
	BORD = 200
	for i in range(1, len(whl)):
		if whl[i][0] > 0.1 and whl[i-1][0] > 0.1:
			if distance(whl[i], whl[i-1]) > JMAX and (whl[i][0] - BORD) * (whl[i-1][0] - BORD) > 0:
				whl[i] = [0,0]

	return whl

def xp(whl):
	return [p[0] for p in whl[0::10] if p[0] > 1]

def yp(whl):
	return [p[1] for p in whl[0::10] if p[0] > 1]

def pairs(path):
	l = []
	for line in open(path):
		ws = line.split(' ')
		if len(ws) > 2:
			continue
		l.append([int(ws[0]) / 480, int(ws[1]) / 480])

	return l

def sb_corners(sbx, sby, rad, angle):
        sbc = []
        #for an in (angle, angle + PI/2, angle + PI, angle + 3*PI/2):
	adif = 2*atan(0.5)
	for an in (angle, angle+adif, angle+PI,angle+PI+adif):
                sbc.append([(sbx + rad * cos(an)), (sby + rad * sin(an))])
        return sbc

SBLW = 5
SBCL = 'green'

def draw_cb(ax):
        for c in range(4):
                ax.plot([sbcorn1[c][0], sbcorn1[c+1][0]], [sbcorn1[c][1]+E2SHY*(1-estart), sbcorn1[c+1][1]+E2SHY*(1-estart)], color=SBCL, linewidth=SBLW)
                ax.plot([sbcorn2[c][0]-E2SH, sbcorn2[c+1][0]-E2SH], [sbcorn2[c][1]+E2SHY*(estart), sbcorn2[c+1][1]+E2SHY*(estart)], color=SBCL, linewidth=SBLW)
        # circle - CB
        CRAD = 74.0
        # circ1 = plt.Circle(((89.0+200*estart)/BS, 85.0/BS),  CRAD / BS, fill = False, color = 'red')
	CLW = 5
	if estart == 0:
	        circ1 = plt.Circle(((84.0), 80.0),  CRAD, fill = False, color = SBCL, linewidth=CLW)
	        circ2 = plt.Circle(((284.0-E2SH), 80.0), CRAD , fill = False, color = SBCL, linewidth=CLW)
	else:
	        circ1 = plt.Circle(((284-E2SH), 80.0),  CRAD, fill = False, color = SBCL, linewidth=CLW)
	        circ2 = plt.Circle(((84), 80.0), CRAD , fill = False, color = SBCL, linewidth=CLW)

        #circ_g1 = plt.Circle((g1x, g1y), 1, color = 'magenta')
        #circ_g2 = plt.Circle((g2x, g2y), 1, color = 'magenta')

        ax.add_artist(circ1)
        ax.add_artist(circ2)
        #ax.add_artist(circ_g1)
        #ax.add_artist(circ_g2)

def postl_trial_path(trial):
	# first trial in first environemnt
	POSTL_TR = trial
	#whl_n = whl_n[:t_n[0][1]] + whl_n[t_n[4][1]:t_n[5][1]]
	whl_n_1 = whl_n[t_n[POSTL_TR][0]:t_n[POSTL_TR][1]]

	# first trial in second environment
	# ORIG = 1/10/6
	ft_2nd_env = trial+1 if '0106' in argv[1] else (10+trial if '1123' in argv[1] else 5+trial) 
	whl_n_2 = whl_n[t_n[ft_2nd_env][0]:t_n[ft_2nd_env][1]]
	# both : only until goal !
	i = 0
	while i < len(whl_n_1):
		dg = distance(whl_n_1[i], [g1x, g1y])
		if dg < RGMIN:
			break
		i += 1
	whl_n_1 = whl_n_1[:i]
	i = 0
	while i < len(whl_n_2):
		dg = distance(whl_n_2[i], [g2x, g2y])
		if dg < RGMIN:
			break
		i += 1
	whl_n_2 = whl_n_2[:i]

	return whl_n_1 + whl_n_2

#=================================================================================================================

if len(argv) < 5:
	print 'USAGE: ()<whl first> <>(whl learning) <>(whl post) <>(whl new learning) <0-SHOW, 1-SAVE>'
	exit(0)

SHOW = bool(int(argv[5]))
argv = resolve_vars(argv + ['%{g1x}', '%{g1y}', '%{g2x}', '%{g2y}', '%{swap}', '%{animal}', '%{day}', ])
sbc = resolve_vars(['%{sb1x}', '%{sb1y}', '%{sb2x}', '%{sb2y}', '%{estart}'])

day = argv[-1]

ld = log_call(argv)

#for i in range(1,5):
#	if 

#print 'WARNING: USING SCALED WHL'
#suf = '.scaled'
suf = ''
#fpath = argv[1].replace('_FULL', '_FIX') if '0429' in argv[1] else argv[1] + suf
fpath = argv[1] + suf
whl_f = whl_to_pos(open(fpath), True)
whl_l = whl_to_pos(open(argv[2] + suf), True)
whl_p = whl_to_pos(open(argv[3] + suf), True)
whl_n = whl_to_pos(open(argv[4] + suf), True)

whl_f = smooth_whl(whl_f)
whl_l = smooth_whl(whl_l)
whl_p = smooth_whl(whl_p)
whl_n = smooth_whl(whl_n)

whl_f = rem_whl_art(whl_f)
whl_l = rem_whl_art(whl_l)
whl_p = rem_whl_art(whl_p)
whl_n = rem_whl_art(whl_n)

g1x = float(argv[6])
g1y = float(argv[7])
g2x = float(argv[8])
g2y = float(argv[9])

#print 'WARNING: adjust goal 2 coords'
#g2x += 7
#g2y += 7

sb1x = float(sbc[0])
sb1y = float(sbc[1])
sb2x = float(sbc[2])
sb2y = float(sbc[3])
estart = int(sbc[4])

swap = bool(int(argv[-3]))
label = argv[-2] + ' - ' + argv[-1]

t_l = pairs(argv[2].replace('_FULL', '') + '.trials')

if '1123' in argv[1]:
	whl_f = whl_l[t_l[1][0]:t_l[1][1]] + whl_l[t_l[11][0]:t_l[11][1]]

if '0301' in argv[1]:
	print 'WARNING: adjsut G1 coords !'
	g1x += 7
	g1y += 2

t_n = pairs(argv[4].replace('_FULL', '') + '.trials')
#print t_n
RGMIN = 8

#print t_l
# whl_l = whl_l[t_l[-1][0]:] + whl_l[t_l[-6][0]:t_l[-5][0]]
# ONLY UNTIL GOAL
whl_l_1 = whl_l[t_l[-11][0]:t_l[-11][1]] if '1123' in argv[1] else whl_l[t_l[-6][0]:t_l[-5][0]]
whl_l_2 = whl_l[t_l[-1][0]:]
i = 0
while i < len(whl_l_1):
        dg = distance(whl_l_1[i], [g1x, g1y])
        if dg < RGMIN:
                break
        i += 1
whl_l_1 = whl_l_1[:i]
i = 0
while i < len(whl_l_2):
        dg = distance(whl_l_2[i], [g2x, g2y])
        if dg < RGMIN:
                break
        i += 1
whl_l_2 = whl_l_2[:i]
whl_l = whl_l_1 + whl_l_2

whl_n0 = postl_trial_path(0)
whl_n1 = postl_trial_path(1)

f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, figsize=(18, 12))

axa = [ax1, ax2, ax3, ax4]

ps = 0.5
#ax1.scatter(xp(whl_f), yp(whl_f), s=ps, color='grey')
#ax2.scatter(xp(whl_l), yp(whl_l), s=ps, color='grey')
#ax3.scatter(xp(whl_p), yp(whl_p), s=ps, color='grey')
#ax4.scatter(xp(whl_n), yp(whl_n), s=ps, color='grey')

E2SH=40
E2SHY=8

# plot 2 parts
#ax1.plot(xp(whl_f), yp(whl_f), color='grey')
plot_by_envs(ax1, xp(whl_f), yp(whl_f))
#ax2.plot(xp(whl_l), yp(whl_l), color='grey')
plot_by_envs(ax2, xp(whl_l), yp(whl_l))
#ax3.plot(xp(whl_p), yp(whl_p), color='grey')
plot_by_envs(ax3, xp(whl_p), yp(whl_p))
#ax4.plot(xp(whl_n), yp(whl_n), color='grey')
plot_by_envs(ax4, xp(whl_n0), yp(whl_n0))
# PLOT 2ND/SECOND TRIAL
#plot_by_envs(ax4, xp(whl_n1), yp(whl_n1), 'black')

for i in range(4):
	plt.sca(axa[i])
	plt.axis('off')

#titles = ['FIRST LEARNING TRIAL', 'LAST LEARNING TRIAL', 'POST-PROBE', 'FIRST TRIAL IN POST-LEARNING']
titles = ['First learning trial', 'Last learning trial', 'Post-probe', 'First trial in post-learning']
lets = ['A', 'B', 'C', 'D']

i = 0
cols = ['r', 'b']
eleg = ['Control', 'Target']

#print 'WARNING: adjust SB coords'
#xd = 10
#yd = 15
#sb1x += xd
#sb1y += yd
#sb2x += xd
#sb2y += yd

for ax in axa:
	# DRAW GOALS
	GOAL_SIZE = 300
	t1 = ax.scatter([g1x], [g1y], s=GOAL_SIZE, color=cols[swap], zorder=10)
	t2 = ax.scatter([g2x-E2SH], [g2y-E2SHY], s=GOAL_SIZE, color=cols[1-swap], zorder=10)
	# legend can cover part of the trajectory, even with the 'best' option
	# ax.legend([t1, t2], [eleg[1-swap],eleg[swap]], loc='best')

	# 10 if no control / target labels
	ax.set_ylim([-10, 220]) # 10 200 / -10 200
	fs = 30

	#ax.text(240 - swap * 200, 0, 'CONTROL', fontsize=fs, color = 'blue')
	#ax.text(30 + swap * 200, 0, 'TARGET', fontsize=fs, color = 'red')

	# figure letters
	#ax.text(-10, 210, lets[i], fontsize = fs + 5)

	# draw start box
	# astart = 1127-65; 1125-75
	# astart2 = 35

	# DEFAULT: -pi/2 -pi/8 left, -pi/8 +pi/4 right - 0304

	# -pi/8, uncom: 0430, com: 1130, 0301
	# 0430 0304 -pi/8-pi/2
	# 1125,1127 -pi/2 
	# 0227 -pi/8 first
	# 0428, 0501, 0227 -pi/8
	asb1 = atan2(sb1y-(80+8*estart), sb1x-(84+200*estart))  -pi/2
	# -pi/8
	# 0430 0304 1127 +pi/8
	# 0227 -pi/8 both
	# 0428, 0501, 0502, 0227 -pi/8
	asb2 = atan2(sb2y-(88-8*estart), sb2x-(284-200*estart)) + pi/8

	astart = asb1#75
	astart2 = asb2#35
	sbrad = 25
        sbcorn1 = sb_corners(sb1x, sb1y, sbrad, astart)
        sbcorn1.append(sbcorn1[0])
        sbcorn2 = sb_corners(sb2x, sb2y, sbrad, astart2)
        sbcorn2.append(sbcorn2[0])
	#for j in range(5):
	#	sbcorn2[j][0] -= E2SH
	draw_cb(ax)

	ax.set_xlim([-7, 337])
	ax.set_ylim([0, 203])
	
	#ax.set_title(titles[i], fontsize=50)
	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)
	i += 1

plt.subplots_adjust(left = 0.02, right = 0.98, top=0.94, bottom=0.02, wspace=0.02)

# debug only
#plt.suptitle(label, fontsize = 20)

if SHOW:
	plt.show()
else:
# plt.savefig(ld + '/TRACK_%s.png' % day)
	plt.savefig('/home/igor/resim/TRACKING/TRACK_%s_REV2.svg' % day)
