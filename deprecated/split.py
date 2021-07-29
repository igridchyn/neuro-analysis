#!/bin/python
import io
from sys import argv

if len(argv) < 2:
	print 'Split 128-channel AXONA bin file into 2 64-channel bin files. Size inconsistency (mod 432 != 0) is ignored).\n(In general: split any binary file into 2 binary files, containing 432-byte chunks in odd and even positions in the original file)'
	usage = argv[0] + ' <binary_file_name>'
	print usage
	exit(1)

name = argv[1]
f128 = io.open(name, 'rb')
f64_1 = io.open(name+'.64.1', 'wb')
f64_2 = io.open(name+'.64.2', 'wb')

CHUNK = 432

while True:
	chunk1 = f128.read(CHUNK)
	if not chunk1: break
	f64_1.write(chunk1)

	chunk2 = f128.read(CHUNK)
	if not chunk2: break
	f64_2.write(chunk2)

f64_1.close()
f64_2.close()
f128.close()
