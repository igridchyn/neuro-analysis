#!/usr/bin/env python
from sys import argv
from math import atan2, cos, sin, pi
import numpy as np
from matplotlib import pyplot as plt
#from call_log import log_call
import os

def rotate(whl, dx, dy, angle, f0 = False):
	whln = []

	for pos in whl:
		if pos[0] < 1000:
			if smaller != (pos[0] < xthold):
				if f0 and (pos[1] > 2 or pos[3] > 2):
					pos[0] = 1023
					pos[1] = 1023
					pos[2] = 1023
					pos[3] = 1023
				whln.append(pos)
				continue

			xsn = pos[0] + dx
			ysn = pos[1] + dy
			xsn1 = xsn*cos(angle) - ysn*sin(angle)
			ysn1 = xsn*sin(angle) + ysn*cos(angle)
		
			xsn = xsn1
			ysn = ysn1		

			if linearize:
				ysn = ylin

			if not smaller:
				xsn += xthold + dx2
		else:
			xsn = pos[0]
			ysn = pos[1]

		if pos[2] < 1000:
			if smaller != (pos[2] < xthold):
				if f0 and (pos[1] > 2 or pos[3] > 2):
					pos[0] = 1023
					pos[1] = 1023
					pos[2] = 1023
					pos[3] = 1023
				whln.append(pos)
				continue

			xbn = pos[2] + dx
			ybn = pos[3] + dy
			xbn1 = xbn*cos(angle) - ybn*sin(angle)
			ybn1 = xbn*sin(angle) + ybn*cos(angle)
		
			xbn = xbn1
			ybn = ybn1

			if linearize:
				ybn = ylin
		
			if not smaller:
				xbn += xthold + dx2
		else:
			xbn = pos[2]
			ybn = pos[3]	
		
		if f0 and (ysn > 2 or ybn > 2):
			xsn = 1023
			ysn = 1023
			xbn = 1023
			ybn = 1023
		whln.append([xsn, ysn, xbn, ybn, pos[4], pos[5]])

	return whln

#=================================================================================================================================
def shift(whln1, both = False, filt = False):
	whln = []
	for pos in whln1:
		ysn = pos[1]
		ybn = pos[3]

		if pos[0] < 1000 or pos[1] < 1000:
			if smaller != (pos[0] < xthold) and not both:
				whln.append(pos)
				continue

			xsn = pos[0] + pdx
		else:
			xsn = pos[0]

		if pos[2] < 1000 or pos[3] < 1000:
			if smaller != (pos[2] < xthold) and not both:
				whln.append(pos)
				continue

			xbn = pos[2] + pdx
		else:
			xbn = pos[2]


		if filt:
			if xsn < 250 and xsn > 150 or xbn < 250 and xbn > 150:
				xsn = 1023
				ysn = 1023
				xbn = 1023
				ybn = 1023
		whln.append([xsn, ysn, xbn, ybn, pos[4], pos[5]])

	return whln
#=================================================================================================================================
def gap(whl):
	# define xthold as a middle of the gap of at least 30
	xmax = int(max([w[0] for w in whl if w[0] != 1023]))
	print('Max x = %d' % xmax)
	xints = [int(w[0]) for w in whl]
	#xints = list(set(xints))
	xis = []
	for i in range(min(xints), xmax):
		if xints.count(i) > 10:
			xis.append(i)
	xints = xis
	print(xints)
	xrstart = 0
	for i in range(min(xints), xmax):
		if i not in xints:
			if xrstart > 0:
				pass
			else:
				xrstart = i
		else:
			if i - xrstart > MINGAP and xrstart > 0:
				glen = i - xrstart
				print('Found gap of length %d starting at %d' % (glen, xrstart))
				return xrstart + (i-xrstart)/2 
			xrstart = 0

	return 0 
#=================================================================================================================================
def angle_and_shifts(whl):
	# automation: find fitting direction (x/y), then project points to line
	xdir = []
	ydir = []
	for pos in whl:
		if pos[0] < 1000:
			if smaller != (pos[0] < xthold):
				continue
			if pos[2] < 1000:
				xdir.append(0.5*(pos[0] + pos[2]))
				ydir.append(0.5*(pos[1] + pos[3]))
			else:
				xdir.append(pos[0])
				ydir.append(pos[1])
		elif pos[2] < 1000:
			if smaller != (pos[2] < xthold):
				continue
			xdir.append(pos[2])
			ydir.append(pos[3])
	xvar = np.std(xdir)
	yvar = np.std(ydir)

	SWITCHED = False
	if yvar > xvar:
		SWITCHED = True
		tmp = xdir
		xdir = ydir
		ydir = tmp

	pol = np.polyfit(xdir, ydir, 1)
	lrange = np.arange(np.min(xdir),np.max(xdir), 1)
	
	fig = plt.figure()
	plt.scatter(xdir, ydir)
	plt.plot(lrange, [x*pol[0] + pol[1] for x in lrange], c='r', lw='4')	
	plt.show()
#	fig.savefig(logdir + 'angle_and_shifts.png')

	print('Pol before: %.2f, %.2f' % (pol[0], pol[1]))
	if SWITCHED:
		tmp = xdir
		xdir = ydir
		ydir = tmp
		p1 = - pol[1] / pol[0]
		p0 = 1.0 / pol[0]
		pol[0] = p0
		pol[1] = p1

	print('Pol after: %.2f, %.2f' % (pol[0], pol[1]))

	# now project to the line
	dx = -np.min(xdir)
	dy = -np.min(ydir)
	angle = -atan2(pol[0], 1)
	print('Angle = %.2f, dx = %.2f, dy = %.2f' % (angle, dx, dy))

	return dx, dy, angle	
#=================================================================================================================================

dx2 = 0

if len(argv) < 4:
	print('Usage: (1)<whl file> (2)<x gap target> (3)<linearize 0/1> (4)<optional : file with transform params>')
	print('Output: (1).new - file with rotated and shifted tracking')
	print('Rotate and shift whl file')
	exit(0)

# read transform params
PARIN = False
if len(argv) == 5:
	vals = []
	PARIN = True
	for line in open(argv[4]):
		if len(line) < 2:
			continue
		vals.append(float(line.split(' ')[1]))
	[xth1, dx1, dy1, a1, pdx1, xth2, dx2, dy2, a2, xth3, pdx2, pdx3] = vals
else:
	parpath = argv[1] + '.params'
	if os.path.isfile(parpath):
		print('ERROR: output params file exists!', patpath)
		exit(1)
	fparams = open(parpath, 'w')

#logdir = log_call(argv)

MINGAP = 30
whl = []
for line in open(argv[1]):
	w = line.split(' ')

	if len(w) < 4:
		continue

	whl.append([float(c) for c in w])

print('len whl', len(whl))

if PARIN:
	xthold = xth1
else:
	xthold = gap(whl)
	fparams.write('XTHOLD %f\n' % xthold)

print('Threshold = %.2f' % xthold)

gapt = float(argv[2])
linearize = bool(int(argv[3]))
ylin = 1

smaller = True
if PARIN:
	[dx, dy, angle] = [dx1, dy1, a1]
else:
	dx, dy, angle = angle_and_shifts(whl)
	fparams.write('DX %f\n' % dx)
	fparams.write('DY %f\n' % dy)
	fparams.write('ANGLE %f\n' % angle)

# increase gap
smaller = False
pdx = 300
print('Shift all > %.2f by %.2f' % (xthold, pdx))
# print 'WARNING! : filtered <250, > 150'
# FOR FIX - last True
whl = shift(whl, False, False)
smaller = True

plt.scatter([w[0] for w in whl], [w[1] for w in whl])
plt.show()

whln = rotate(whl, dx, dy, angle)
# separately align to match the range:
whln1 = whln[:]
if PARIN:
	pdx = pdx1
else:
	pdx = min([w[0] for w in whln1])
	fparams.write('PDX %f\n' % pdx)
whln = shift(whln1)

smaller = False
if PARIN:
	xthold = xth2
	[dx, dy, angle] = [dx2, dy2, a2]
else:
	xthold = gap(whln)
	dx, dy, angle = angle_and_shifts(whln)
	# !!!!
	dx=100
	fparams.write('XTHOLD2 %f\n' % xthold)
	fparams.write('DX2 %f\n' % dx)
	fparams.write('DY2 %f\n' % dy)
	fparams.write('ANGLE2 %f\n' % angle)	

print('len whln', len(whln))
print('WARNING: DX set to 100, gap(xthold) = ', xthold)
dx2 = 0
# !!! FOR FIX - True
whln = rotate(whln, dx, dy, angle, False)

print('After rotation ...')

plt.figure()
plt.scatter([w[0] for w in whln], [w[1] for w in whln])
plt.show()

# don't know min_2 after rotation
if PARIN:
	xthold = xth3
else:
	xthold = gap(whln)
	fparams.write('XTHOLD3 %f\n' % xthold)
print('XTHOLD = ', xthold)
# TODO: use both small / big
max1 = max([w[0] for w in whln if w[0] < xthold])
min2 = min([w[0] for w in whln if w[0] > xthold])
print('Max1 = %.2f, Min2 = %.2f' % (max1, min2))

if PARIN:
	pdx = pdx2
else:
	pdx = max1 - min2 + gapt
	fparams.write('PDX2 %f\n' % pdx)

whln = shift(whln)

# add most negative x
minx = min([w[0] for w in whln])
if PARIN:
	pdx = pdx3
else:
	pdx = -minx
	fparams.write('PDX3 %f\n' % pdx)
whln = shift(whln, True)

newpath = argv[1] + '.new'
if os.path.isfile(newpath):
	print('ERROR: output file exists', newpath)
	exit(1)
fn = open(newpath, 'w')
for pos in whln:
	fn.write(' '.join([str(pos[0]), str(pos[1]), str(pos[2]), str(pos[3]), str(int(pos[4])), str(int(pos[5]))]) + '\n')

opath = argv[1] + '.original'
if os.path.isfile(opath):
	i = 1
	opath = argv[1] + '.original.' + str(i)
	while os.path.isfile(opath):
		i += 1
		opath = argv[1] + '.original.' + str(i)
	print('Written original to ', opath)

#os.rename(argv[1], opath)	
os.rename(argv[1] + '.new', argv[1] + '.linear')
