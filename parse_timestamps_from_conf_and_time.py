#!/usr/bin/env python

from sys import argv

if len(argv) < 6:
	print 'usage: (1)<timestamps file> (2)<confidences file> (3)<confidence threshold> (4)<0/1 : more / less than threshold> (5)<output name>'
	exit(0)

fc = open(argv[2])
ft = open(argv[1])
CTHOLD = float(argv[3])
more = argv[4] == '0'

fo = open(argv[5], 'w')

ltime = ft.readline()
while len(ltime) > 0:
	lconf = fc.readline()
	conf = float(lconf)

	if (conf > CTHOLD) != more:
		fo.write(ltime)

	ltime = ft.readline()
		
