#!/usr/bin/env python

from sys import argv

if len(argv) < 2:
	print 'USAGE: (1)<path to whl file>'
	print 'SET Y-COORD to 1 (for known locations)'
	exit(0)

path = argv[1]

fo = open(path + '.cset', 'w')
for line in open(path):
	ws = line.split(' ')
	if len(ws) < 5:
		print 'Skip ' + line
		continue

	if float(ws[1]) != 1023:
		ws[1] = '1'

	if float(ws[3]) != 1023:
		ws[3] = '1'

	fo.write(' '.join(ws) + '\n')

fo.close()
