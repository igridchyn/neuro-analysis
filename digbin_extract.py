#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
import struct

if len(argv) < 3:
	print('USAGE: (1)<digbin file> (2)<timestamps out file>')
	exit(0)

f = open(argv[1], 'rb')
fo = open(argv[2], 'w')

t = 0
ts = 0
dig_prev = 0

STATE = False

while True:
	s = f.read(2)
	if not s:
		break

	dig = struct.unpack('h', s)[0]
	
	if dig != dig_prev:
		STATE = not STATE

		dig_prev = dig

		ts_prev = ts
		ts = t/4*3

		if dig == 2:
		    print(ts, dig)
			#fo.write('%d\n' % ts)
			fo.write('%d %d\n' % (ts_prev, ts))
	t += 1
