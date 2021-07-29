#!/usr/bin/env python

import os
import glob
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from numpy import log, exp
import struct
from random import shuffle

def read_shuffle_write(tetr, nfet):
	f = open(argv[2] + '.fetb.' + str(tetr), 'rb')
	fo = open(argv[2] + '_shuffled.fetb.' + str(tetr), 'wb')
	feats = []
	times = []

	#for i in range(100):
	while True:
		buf = f.read(4*nfet)
		if not buf:
			break
		ar = struct.unpack('f'*nfet, buf) 
		feats.append(ar)
		times.append(struct.unpack('i', f.read(4))[0])

	print 'Read %d spikes, shuffle and write' % len(times)
	print times[0:20]

	# print feats, times, '\n\n\n\n\n'
	shuffle(feats)
	#print feats

	# write back
	for i in range(len(times)):
		fo.write(struct.pack('f'*nfet, *feats[i]))
		fo.write(struct.pack('i', times[i]))
	fo.close()
	f.close()

#====================================================================================================

if len(argv) < 3:
	print 'Usage: (1)<tetrode config> (2)<fetb prefix>'
	print 'Output: (2)_shuffled.fetb'
	print 'Shuffle times of all spikes within each tetrode, information in tetrode config must correspond to the content of fetb files'
	exit(0)

ftetr = open(argv[1])
nt = int(ftetr.readline())
print '%d tetrodes' % nt

for t in range(nt):
	nchan = int(ftetr.readline())
	print '%d channels in tetr %d' % (nchan, t)
	nfet = 2 * nchan + 4
	read_shuffle_write(t, nfet)
	ftetr.readline()
