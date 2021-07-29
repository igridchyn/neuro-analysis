#!/usr/bin/env python

# extract decoded windows before or after ... (first and last)

from sys import argv

if len(argv) < 4:
	print 'USAGE: (1)<input> (2)<output> (3)<F / L>'
	print 'EXTRACT SUB-SET OF SWRDEC: ALL FIRST OR ALL LAST WINDOWS'
	exit(0)

first = argv[3] == 'F'

fout = open(argv[2], 'w')
curswr = -1
prevline = ''

for line in open(argv[1]):
	swri = int(line.split(' ')[0])

	if swri > curswr:
		if first:
			fout.write(line)
		elif curswr > -1:
			fout.write(prevline)

		curswr = swri

	prevline = line	
