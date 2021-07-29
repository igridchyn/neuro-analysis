#!/usr/bin/env python

from sys import argv

if len(argv) < 2:
	print 'USAGE: (1)<whl file>'
	print 'DUPLICATE first LED in the file'
	exit(0)

f = open(argv[1])
fo = open(argv[1] + '.dup', 'w')

for line in f:
	ws = line.split(' ')
	if len(ws) == 0:
		continue

	fo.write(' '.join([ws[2], ws[3], ws[2], ws[3], ws[4], ws[5]]))
