#!/usr/bin/env python
from sys import argv
import os

if len(argv) < 2:
	print 'Output number os clustes per tetrode and in total'
	print argv[0] + ' basename'

base = argv[1] + '.clu'
cluns=[]

for i in range(1, 16):
	filename = base + str(i)
	if not os.path.isfile(filename):
		continue
	f = open(filename)
	cluns.append(int(f.readline()[:-1]) - 1)

print cluns
print sum(cluns)
