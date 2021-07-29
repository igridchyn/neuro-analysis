#!/usr/bin/env python

from sys import argv

sstr = str(len(argv) - 1)
total = 0
for s in argv[1:]:
	print s, ':'

	f = open(s + '/session_shifts.txt')
	sesdur = 0
	for line in f:
		sesdur = int(line)
		print total + sesdur

	total += sesdur
	sstr += ' ' + str(total)

print sstr
