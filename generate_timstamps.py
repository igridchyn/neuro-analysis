#!/usr/bin/env python

from sys import argv

if len(argv) < 5:
	print 'Usage:' + argv[0] + '(1)<output> (2)<start (samples)> (3)<interval> (4)<end>'
	exit(0)

f = open(argv[1], 'w')
start = int(argv[2])
interval = int(argv[3])
end = int(argv[4])

time = start
while time <= end:
	f.write(str(time) + '\n')
	time += interval
f.close()
