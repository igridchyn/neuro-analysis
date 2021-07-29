#!/usr/bin/env python
from sys import argv
import os
from iutils import resolve_vars

if len(argv) < 2:
	print 'USAGE: (1)< whl file >'
	print 'HC: scale transform with scales different for 2 environments (which one ins started is read from about.txt'
	exit(0)

f = open(argv[1])
fo = open(argv[1] + '.scaled', 'w')

XB = 200

abpath = 'about.txt'
if not os.path.isfile(abpath):
	abpath = '../about.txt'
	if not os.path.isfile(abpath):
		print 'ERROR: about.txt not found'
		exit(1)

env = int(resolve_vars(['%{estart}'])[0])
print env
# starting env = ENV1
if env == 0:
	scale2 = 1.039132
	scale1 = 1.16
# starting env = ENV2
else:
	scale1 = 1.039132
	scale2 = 1.16

for line in f:
	whl = line[:-1].split(' ')

	if len(whl) < 5:
		break

	# print whl
	xb = float(whl[0])
	yb = float(whl[1])
	xs = float(whl[2])
	ys = float(whl[3])
	id = int(whl[4])
	v = int(whl[5])


	# if valid position in second environment
	if xb < 1000:
		if xb < XB:
			xb *= scale1
			yb *= scale1
			#xb = 1023
			#yb = 1023
		else:	
			xb = (xb-XB) * scale2 + XB
			yb *= scale2
	else:
		pass

	if xs < 1000:
		if xs < XB:
			ys *= scale1
			xs *= scale1
			#xs = 1023
			#ys = 1023
		else:
			xs = (xs-XB) * scale2 + XB
			ys *= scale2
	
	fo.write(str(xb) + ' ')
	fo.write(str(yb) + ' ')
	fo.write(str(xs) + ' ')
	fo.write(str(ys) + ' ')
	fo.write(str(id) + ' ')
	fo.write(str(v) + '\n')

f.close()
fo.close()
