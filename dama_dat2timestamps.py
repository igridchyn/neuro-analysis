#!/usr/bin/env python

from sys import argv
import struct

if len(argv) < 6:
	print '(1)<DAT file> (2)<total number of channels> (3)<channel with digital input (0-based)> (4)<sampling rate> (5)<output file>'
	print 'Extract intervals when given cahannel in the dat file was non-0'
	exit(0)

f = open(argv[1], 'rb')
nchan = int(argv[2])
chandig = int(argv[3])
sr = int(argv[4])
fout = open(argv[5], 'w')

state = False
start = 0

t = 0
while True:
	buf = f.read(2 * nchan)
	if not buf:
		break
	ar = struct.unpack('h' * nchan, buf)
	dig = ar[chandig]
	
	# pulse over
	if dig == 0 and state:
		state = False
		fout.write('%d %d\n' % (tstart, t))

	# pulse start
	if dig > 0 and not state:
		tstart = t
		state = True

	t += 1

fout.close()
f.close()
