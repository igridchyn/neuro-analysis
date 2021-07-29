#!/usr/bin/env python

from sys import argv

if len(argv) < 4:
	print 'USAGE: (1)<path1> (2)<path2> (3)<merged list>'
	exit(0)

path1 = argv[1]
path2 = argv[2]

t1 = [int(t) for t in open(path1)]
t2 = [int(t) for t in open(path2)]

t12 = sorted(t1 + t2)

fout = open(argv[3], 'w')
for t in t12:
	fout.write(str(t) + '\n')
