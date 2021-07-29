#!/usr/bin/env python

from sys import argv
import os

if not os.path.isfile(argv[1]): #or os.path.isfile(argv[2]):
	print 'ERROR: input file doesnt exist or output file exists'
	exit(1)

fab = open(argv[1])
fabn = open(argv[2], 'w')

d = {}
for line in fab:
	if len(line) < 1:
		continue

	ws = line.split(' ')

	d[ws[0]] = ws[1][:-1]

print d

if d['estart'] == '0':
	print 'Start env = E1'
	s1 = 1.16
	s2 = 1.039
else:
	print 'Start env = E2'
	s1 = 1.039
	s2 = 1.16
		
d['g1x'] = float(d['g1x']) * s1
d['g1y'] = float(d['g1y']) * s1
d['g2x'] = (float(d['g2x']) - 200) * s2 + 200
d['g2y'] = (float(d['g2y'])) * s2
d['sb1x'] = float(d['sb1x']) * s1
d['sb1y'] = float(d['sb1y']) * s1
d['sb2x'] = (float(d['sb2x']) - 200) * s2 + 200
d['sb2y'] = (float(d['sb2y'])) * s2

print d

for key in d:
	fabn.write(str(key) + ' ' + str(d[key])+ '\n')
fabn.close()
