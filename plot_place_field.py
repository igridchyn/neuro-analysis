#!/usr/bin/env python3

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
from math import pi, cos, sin
import matplotlib.gridspec as gridspec
#from iutils import *
PI = pi

#for path in argv[1:]:

#	m = np.genfromtxt(path)
#	m *= 50

#	fig = plt.figure(figsize = (20, 8))

#	plt.imshow(m[6:, range(6,36) + range(60,m.shape[1])], interpolation = 'nearest', origin='lower')

#	ax = plt.gca()
	#ax.set_aspect(0.5)

#	cb = plt.colorbar()#orientation = 'horizontal')
#	cb.ax.tick_params(labelsize=20)

#	plt.savefig(path.replace('mat', 'png'))
#	plt.close(fig)

	# plt.show()

def sb_corners(sbx, sby, rad, angle):
	sbc = []
	for an in (angle, angle + PI/2, angle + PI, angle + 3*PI/2):
		sbc.append([(sbx + rad * cos(an))/BS, (sby + rad * sin(an))/BS])
	return sbc

def draw_cb(ax):
	if PLOTSB:
		for c in range(4):
			ax.plot([sbcorn1[c][0], sbcorn1[c+1][0]], [sbcorn1[c][1], sbcorn1[c+1][1]], color=SBCL, linewidth=SBLW)
			ax.plot([sbcorn2[c][0], sbcorn2[c+1][0]], [sbcorn2[c][1], sbcorn2[c+1][1]], color=SBCL, linewidth=SBLW)
	# circle - CB
	CRAD = 74.0
	# circ1 = plt.Circle(((89.0+200*estart)/BS, 85.0/BS),  CRAD / BS, fill = False, color = 'red')
	#circ1 = plt.Circle(((84.0+200*estart)/BS, 80.0/BS),  CRAD / BS, fill = False, color = 'red')
#	circ2 = plt.Circle(((284.0-200*estart)/BS, 88.0/BS), CRAD / BS, fill = False, color = 'red')

	#circ_g1 = plt.Circle((g1x/BS, g1y/BS), 1.5, color = 'white')
#	circ_g2 = plt.Circle((g2x/BS, g2y/BS), 1.5, color = 'white')

#	ax.add_artist(circ1)
#	ax.add_artist(circ2)
#	ax.add_artist(circ_g1)
#	ax.add_artist(circ_g2)

	ax.set_xlim([0, 66])
	ax.set_ylim([0, 33])

	ax.set_xticks([],[])
	ax.set_yticks([],[])

	E0SHIFTS = {'jc181' :-16, 'jc182':-16, 'jc184':-16, 'jc188':-16}
	E1SHIFTS = {'jc181' :0,   'jc182':  0, 'jc184':-16, 'jc188':-16}
	ESHIFTS = [E0SHIFTS, E1SHIFTS]

	TY = 28
	# 16
	# E2SHIFT = 0
	# estart
	#esvar = int(estart != swap)
	#esvar = int(estart)
	#ax.text(1  + swap*33 + esvar * E2SHIFT, TY, 'TARG', color='red', fontsize=25)
	#ax.text(34 - swap*33 + (1-esvar) * E2SHIFT, TY, 'CONT', color='blue', fontsize=25)
	#ax.text(16  + swap*33 + ESHIFTS[esvar][animal], TY, 'TARG', color='red', fontsize=25)
	#ax.text(50  - swap*33 + ESHIFTS[1-esvar][animal], TY, 'CONT', color='blue', fontsize=25)

def scale_envwise(m):
	# DOF: scale each half on it's own
	m[np.isinf(m)] = np.nan
	hx = m.shape[1] / 2
	m1 = np.nanmax(m[:,:hx])
	m2 = np.nanmax(m[:,hx:])
	if not np.isnan(m1) and m1 > 0.00000000001:
		m[:,:hx] /= m1
	if not np.isnan(m2) and m2 > 0.00000000001:
		m[:,hx:] /= m2
	return m, m1, m2

def scale_common(m):
	m[np.isinf(m)] = np.nan
	m1 = np.nanmax(m)
	if not np.isnan(m1) and m1 > 0.00000000001:
		m /= m1
	return m, m1

#====================================================================================================================================================================================================
#suppress_warnings()

SBLW = 3
SBCL = 'red'
ALL = True
BS = 6

day = ''
animal = ''

# read SB coordinates
#fa = open('../../about_old.txt')
#for line in fa:
#	ws = line.split(' ')
#	if ws[0] == 'sb1x':
#		sb1x = float(ws[1])
#	elif ws[0] == 'sb1y':
#		sb1y = float(ws[1])
#	elif ws[0] == 'sb2x':
#		sb2x = float(ws[1])
#	elif ws[0] == 'sb2y':
#		sb2y = float(ws[1])
#	elif ws[0] == 'estart':
#		estart = int(ws[1])
#	elif ws[0] == 'swap':
#		swap = int(ws[1])
#	elif ws[0] == 'g1x':
#		g1x = float(ws[1])
#	elif ws[0] == 'g1y':
#		g1y = float(ws[1])
#	elif ws[0] == 'g2x':
#		g2x = float(ws[1])
#	elif ws[0] == 'g2y':
#		g2y = float(ws[1])
#	elif ws[0] == 'animal':
#		animal = ws[1][:-1]
#	elif ws[0] == 'date':
#		day = ws[1][2:-1]

# find first startring with '-'
i = 1
while i < len(argv) and argv[i][0] != '-':
	i+=1

PLOTSB = False

#op = parse_optional_params(argv[i:])
op = {}
#DISP_TITLES = bool(gdvi(op, 'dt', 0))
DISP_TITLES = False

for path in argv[1:]:
	if path.startswith('-'):
		print('Stop after params starting with -')
		break

	m = np.genfromtxt(path)
	m *= 50
	mx = np.nanmax(m)

	#fig = plt.figure(figsize = (20, 8))

	# full or partial
	NSCOL = 4
	if ALL:
		# for 5 figures
		#fig, axarr = plt.subplots(2, NSCOL, figsize=(20, 9), squeeze=False)
		# 2 X 2 sessions
		#fig, axarr = plt.subplots(2, NSCOL, figsize=(14, 8), squeeze=False)
		# 1 x 4 sessions
		fig, axarr = plt.subplots(1, NSCOL, figsize=(28, 3.5), squeeze=False)
	else:
		fig, axarr = plt.subplots(2, 1) #, figsize=(8, 20))

	#gs1 = gridspec.GridSpec(2, 3)
	#gs1.update(wspace=0.025, hspace=0.001)

	#yrange = range(6,36) + range(60,m.shape[1])
	yrange = range(0,m.shape[1])
	# was [6:, ...
	titles = ['Trash', 'Learning, 1st half', 'Learning, 2nd half', 'Post-probe', 'Post-learning, 1st trial', 'Post-learning, 2nd half']

	# draw start box
	if PLOTSB:
		sbcorn1 = sb_corners(sb1x, sb1y, 20, 0.2)
		sbcorn1.append(sbcorn1[0])
		sbcorn2 = sb_corners(sb2x, sb2y, 20, 0.2)
		sbcorn2.append(sbcorn2[0])

	# DEBUG
	#print m.shape

	SCALE_ENVWISE = False
	if SCALE_ENVWISE:
		m, mx1, mx2 = scale_envwise(m)
	else:
		m, mx2 = scale_common(m)

	if ALL:
		axarr[0, 0].imshow(m[:, yrange], interpolation = 'nearest', origin='lower')
		if DISP_TITLES:
			axarr[0, 0].set_title(titles[2], fontsize = 25)
		rfs = 25
		if SCALE_ENVWISE:
			axarr[0, 0].text(27, 2, '%.1f' % mx1, fontsize=rfs)
		axarr[0, 0].text(57, 2, '%.1f' % mx2, fontsize=rfs)
		draw_cb(axarr[0,0])
		
		axarr[0,0].axis('off')
	else:
		axarr[0].set_title(titles[0], fontsize = 25)
		axarr[0].imshow(m[:, yrange], interpolation = 'nearest', origin='lower')
		draw_cb(axarr[0])


	# all al part of sessions
	for i in range(3, 6):
	#for i in range(3,4):
		pathi = path.replace('_2.', '_' + str(i) + '.')
		m = np.genfromtxt(pathi)
		m *= 50
		
		if SCALE_ENVWISE:
			m, mx1, mx2 = scale_envwise(m)
		else:
			m, mx2 = scale_common(m)

		smax = np.nanmax(m)
		if smax > mx:
			mx = smax
		# was [6:, ...

		# axix index
		if ALL:
			ai = i - 2
			a = axarr[ai//NSCOL, ai%NSCOL].imshow(m[:, yrange], interpolation = 'nearest', origin='lower')
			if DISP_TITLES:
				axarr[ai//NSCOL, ai%NSCOL].set_title(titles[i], fontsize = 25)
			draw_cb(axarr[ai//NSCOL, ai%NSCOL])
			rfs = 25
			if SCALE_ENVWISE:
				axarr[ai//NSCOL, ai%NSCOL].text(27, 2, '%.1f' % mx1, fontsize=rfs)
			axarr[ai//NSCOL, ai%NSCOL].text(57, 2, '%.1f' % mx2, fontsize=rfs)

			#axarr[ai/NSCOL, ai%NSCOL].patch.set_visible(False)	
			axarr[ai//NSCOL, ai%NSCOL].axis('off')
		else:
			ai = i - 2
			a = axarr[ai].imshow(m[:, yrange], interpolation = 'nearest', origin='lower')
			axarr[ai].set_title(titles[i - 1], fontsize = 25)
			draw_cb(axarr[ai])

		# fig.colorbar(a, orientation = 'vertical')

	#if ALL:
	#	fig.delaxes(axarr[1,2])

	# axarr[-1, -1].axis('off')

	ax = plt.gca()
	#ax.set_aspect(0.5)

	#cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
	#fig.colorbar(a, orientation = 'vertical')

	#cb = plt.colorbar()#orientation = 'horizontal')
	# cb.ax.tick_params(labelsize=20)

	#fig.tight_layout()
	#plt.subplots_adjust(hspace=0, wspace=0)

	#plt.savefig(path.replace('mat', 'png'))
	#plt.savefig('/home/igor/resim/FIG3/PFS/' + path.replace('mat', 'png'))
	#path = ('%s_%s_' % (animal, day)) + path
	plt.subplots_adjust(left=0.01, top=0.98, right=0.99, bottom=0)
	# plt.savefig('/home/igor/resim/_AUTOSAVE/' + path.replace('mat', 'svg'))
	#print 'FIGURE SAVED'
	
	plt.show()
	#plt.close(fig)

	#exit(0)
