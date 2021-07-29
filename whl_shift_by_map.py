#!/usr/bin/env python
from sys import argv
import numpy as np

def wpos(pos):
	if pos[0] == 1023 and pos[2]==1023:
		return 1023, 1023

	if pos[0] == 1023:
		return pos[2], pos[3]

	if pos[2] == 1023:
		return pos[0], pos[1]

	return (pos[0]+pos[2])/2, (pos[1]+pos[3])/2

if len(argv) < 4:
	print 'Usage: <1>(whl file path) <2>(map 1 path [remaining positions]) <3>(map 2 path [shifting positions]) <4>(bin size) <5>(shift)'
	exit(0)

whl = []
f = open(argv[1])
for line in f:
        if len(line) < 5:
                continue
        whl.append([float(w) for w in line.split(' ')])

m1 = np.loadtxt(argv[2])
m2 = np.loadtxt(argv[3])

print 'Size of matrices: ', m1.shape, m2.shape

binsize = float(argv[4])
shift = float(argv[5])

whln = []
for pos in whl:
	x, y = wpos(pos)
	if x == 1023:
		whln.append(pos)
		continue

	bx = x / binsize
	by = y / binsize

	if by >= m2.shape[0] or bx >= m2.shape[1]:
		print 'Ignore coord, OOR'
		whln.append([1023, 1023, 1023, 1023, pos[-2], pos[-1]])
		continue
		

	if m2[by,bx] > 0:
		posn = []
		if pos[0] != 1023:
			posn.extend([pos[0] + shift, pos[1]])
		else:
			posn.extend([1023, 1023])
		if pos[2] != 1023:
			posn.extend([pos[2] + shift, pos[3]])
		else:
			posn.extend([1023, 1023])
		
		posn.extend(pos[-2:])
		whln.append(posn)
		continue
	
	if m1[by,bx] > 0:
		whln.append(pos)
		continue

	whln.append([1023, 1023, 1023, 1023, pos[-2], pos[-1]])
	
# print whln
fo = open(argv[1] + '.shift', 'w')
for l in whln:
	if len(l) < 6:
		print l
	fo.write(' '.join([str(s) for s in l[0:4]]) + ' ' + str(int(l[4])) + ' ' + str(int(l[5])) + '\n')
