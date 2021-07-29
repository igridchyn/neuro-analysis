#!/usr/bin/env python
from sys import argv

if len(argv) < 3:
	print 'Show IDs of clusters with <= <threshold> elements'
	print "Arguments: <path inclusing extension and cluster number> <threshold>"
	exit()

path = argv[1]
THOLD = int(argv[2])

f = open(path)
ls = f.read().split('\n')
clun = int(ls[0])
ls = ls[1:-1]

print clun, ' clusters'

scounts = [0] * (clun + 1)

for l in ls:
	scounts[int(l)] += 1


small_inds = [i for i in range(0, clun + 1) if scounts[i] < THOLD]

print 'Indices of clusters with less than ', THOLD, ' elements:'
print small_inds
