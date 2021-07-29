#!/usr/bin/env python

import os
from sys import argv
import struct
import numpy as np

if len(argv) < 3:
	print 'USAGE: (1)<fet base> (2)<output file: total res>'
	print 'GENERATE TOTAL RES FILE OUT OF THE SPIKE TIMESTAMPS IN THE FET FILES, NEEDS TETR CONFIG'
	exit(0)

# read tetrode config - number of channels per tetrode
cwd = os.getcwd()
dirs = cwd.split('/')
ses = dirs[-1]
day = dirs[-2]
an = dirs[-3]

tconfpath = '/home/igor/code/ews/lfp_online/sdl_example/Res/tetr/tetr_' + an + '_' + day + '.conf'
if 'FULL' in ses:
	tconfpath = tconfpath.replace('.conf', '_full.conf')
	print 'WARNING: USING FULL TETRODE CONFIG!'

if not os.path.isfile(tconfpath):
	print 'Cannot find the tetrode config at ', tconfpath
	exit(1)
ftconf = open(tconfpath)
ftconf.readline()
nchan = []
for line in ftconf:
	if len(line) > 4:
		continue
	else:
		nchan.append(int(line))
print nchan

ares = []
#nfet = 12
tetr = 0
while os.path.isfile(argv[1] + str(tetr)):
        print 'Read fet', tetr
	nfet = nchan[tetr] * 2 + 4
        f = open(argv[1] + str(tetr), 'rb')
        tetr += 1
        ares.append([])
        while True:
                        buf = f.read(4*nfet)
                        if not buf:
                                break
			if len(buf) < 4 * nfet:
				print 'BUFFER CUT!'
				continue
                        ar = struct.unpack('f'*nfet, buf)
                        # feats.append(ar)
			buf = f.read(4)
			if len(buf) < 4:
				print 'BUFFER I CUT!'
				continue
                        ares[-1].append(struct.unpack('i', buf)[0])

	# DEBUG
	#print ares[-1]

# merge res
ires = [0] * len(ares)
res = []

LR = len(ares)

DUM = 9000000000
for i in range(LR):
	ares[i].append(DUM)

print 'LR = %d' % LR

while True:
	ra = [ares[i][ires[i]] for i in range(LR)]
	mn = min(ra)
	am = np.argmin(ra)
	ires[am] += 1

	if mn == DUM:
		break
	else:
		res.append(mn)

fout = open(argv[2], 'w')
for r in res:
	fout.write(str(r) + '\n')
fout.close()
