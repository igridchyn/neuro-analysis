#!/usr/bin/env python

import struct
from sys import argv
import os

if len(argv) < 6:
	print 'USAGE: (1)<timestamps file> (2)<fet file base> (3)<time before, ms> (4)<time after, ms> (5)<output file>'
	print 'CALCULATE NUMBER OF SPIKES IN THE GIVEN TIMEWINDOW AROUND GIVEN TIMESTAMPS'
	exit(0)

ts = [int(l) for l in open(argv[1])]
# res = [int(l) for l in open(argv[2])]
ares = []
nfet = 12
tetr = 0
while os.path.isfile(argv[2] + str(tetr)):
	f = open(argv[2] + str(tetr), 'rb')
	tetr += 1
	ares.append([])
	while True:
			buf = f.read(4*nfet)
			if not buf:
				break
			ar = struct.unpack('f'*nfet, buf)
			# feats.append(ar)
			ares[-1].append(struct.unpack('i', f.read(4))[0])
	print 'Read fet', tetr

tbef = int(argv[3]) * 24
taft= int(argv[4]) * 24
nspikes = [0] * len(ts)

for tet in range(tetr):
	res = ares[tet]
	ires = 0
	it = 0
	for t in ts:
		while ires < len(res) and res[ires] < t - tbef:
			ires += 1
		istart = ires
		while ires < len(res) and res[ires] < t + taft:	
			ires += 1

		nspikes[it] += ires - istart
		it += 1

# print nspikes

fout = open(argv[5], 'w')
for ns in nspikes:
	fout.write(str(ns) + '\n')
fout.close()
