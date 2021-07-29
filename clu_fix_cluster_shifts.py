#!/usr/bin/env python

from sys import argv

if len(argv) < 3:
	print '(1)<clu file to fix> (2)<starting clu number INCLUSIVE>'
	exit(0)

f = open(argv[1])
fo = open(argv[1] + '.fix', 'w')

CS = int(argv[2])

for line in f:
	c = int(line)
	if c >= CS:
		c += 1

	fo.write(str(c) + '\n')

f.close()
fo.close()
