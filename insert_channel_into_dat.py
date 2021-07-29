#!/usr/bin/env python

from sys import argv
import struct

if len(argv) < 6:
	print 'Usage: ' + argv[0] + ' (1)<input file> (2)<output file> (3)<position to insert, 0-based> (4)<value to insert (as signed short)> (5)<number of channels in the input file>'
	print 'Insert dummy channel data to insert into dat-file (create to fix missing channel in the recording)'
	exit(0)

fi = open(argv[1], 'rb')
fo = open(argv[2], 'wb')
# insert at this pos
pos = int(argv[3])
val = int(argv[4])
# total number of channels in the input file
chan = int(argv[5])

if pos >= chan:
	print 'ERROR: position should be less than number of channels'
	exit(1)

packval = struct.pack('h', val)
print 'Size of the packed value: %d' % struct.calcsize('h')
print 'Insert value %s at position %d in the file %s' % (packval, pos, argv[1])

dbytes = "DUMMY"

try:
	while dbytes != "":
		if pos > 0:
			dbytes = fi.read(2*pos)
			fo.write(dbytes)
			
		# fo.write(struct.pack('h', val))
		# fo.write(bytes([0]))
		fo.write(struct.pack('h', 0))

		if chan - pos > 0:
			dbytes = fi.read(2*(chan - pos))
			fo.write(dbytes)
finally:
	print 'Close both files'
	fi.close()
	fo.close()
