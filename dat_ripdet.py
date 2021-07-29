#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *
import struct

if len(argv) < 4:
	print 'USAGE: (1)<filtetred signal file - main> (2)<filtered signal file-reference> (2)<number of SD>'
	exit(0)

# calculate mean / std of the power
path = argv[1]
pathref = argv[2]
HAVEREF = (pathref != '-')
f = open(path, 'rb')
if HAVEREF:
    fr = open(pathref, 'rb')
#f = open(path + '.main', 'rb')
#fr = open(path + '.ref', 'rb')
batch = 1000*1000 # 1M
eof = False
dat = []
mean = 0
std = 0
# first collect data to calculate mean / std, later detect
detmode = False

# running window containing 16 samples
lrunar = 307
runar = lrunar * [0]
irunar = 0

# to estimate powers mean / std - as mean of squares of filtered signal in the 307 window ( = window of 16 at 1.25 KHz)
pows = []
PSC = 5000.0

# read mean std from file if exitst
if os.path.isfile(path + '.msd'):
	amsd = np.loadtxt(path + '.msd')
	mean = amsd[0] #/ PSC
	std   = amsd[1] #/ PSC
	print 'Read mean / std from file:', mean, std
	detmode = True
else:
    print('Will calculate mean and std')

tshift = 0
lastdet = 0

# where the minor threshold has been exceeded
lastswstart = 0
# to detect the first one properly 
lastswend = 1
minthold = 1.0
NSD = float(argv[3])

# detection refractory period - like with the sync
detref = 0

tswr = []

sthold = argv[3]
fosw = open(path + '.' + sthold + '.sw', 'w')
#fop = open(path + '.rpow', 'w')
#fdb = open(path + '.debug', 'w')
foswi = open(path + '.' + sthold + '.swi', 'w')

#prevdat = batch * [0]

while not eof:
	neof = f.read(2*batch)
        if HAVEREF:
    	    neofr = fr.read(2*batch)
	if len(neof) < batch:
		eof = True
		batch = len(neof)
		break

	bdatm = struct.unpack('%dh' % batch, neof)
        if HAVEREF:
    	    bdatr = struct.unpack('%dh' % batch, neofr)
	    bdat = [(bdatm[i] - bdatr[i]) for i in range(len(bdatm))]
        else:
            bdat = bdatm[:]

	#prevdat = dat[:]
	if detmode:
		dat = bdat
	else:
		dat.extend(bdat)
	print '.'

	# update array for power calculation
	for i in range(batch):
		runar[irunar] = (dat[-batch + i] ** 2) / float(lrunar) / PSC
		irunar = (irunar + 1) % lrunar
		pows.append(sum(runar)) #  / lrunar)
		
		#if tshift + i > 769580 and tshift + i < 786400:
		#	fdb.write('%d %f %d %f\n' % (tshift+i, pows[-1], lastdet, mean + NSD * std))

		if detmode:
			# cross threshold AND after refractory AND previous over
			if (pows[-1] > mean + NSD * std) and (tshift + i - lrunar / 2 - lastdet > detref) and (lastswend > 0):
				# tswr.append(tshift + i - lrunar / 2)
				print 'Detected major threshold cross at', tshift + i - lrunar / 2
				lastdet = tshift + i - lrunar / 2

				# find minor threshold crossing
				ip = -2
				while (ip > -batch) and (pows[ip] > mean + minthold * std):
					ip -= 1
				lastswstart = tshift + i - lrunar / 2 + ip
				# to define later
				lastswend = 0

				#fosw.write('%d %d %d\n' % (lastswstart, lastdet, lastswend))
				#fosw.write('%d\n' % lastdet)

			# if looking for end, check if dropped	
			if (lastswend == 0) and (pows[-1] < mean + minthold * std):
				lastswend = tshift + i - lrunar / 2

				# min duration - 40 ms
				#if lastswend - lastswstart > 960:
                                # !!! CENTER OF THE WINDOW !!!
				fosw.write('%d %d %d\n' % (lastswstart, lastdet, lastswend))

				# properties - number of cycles, frequency
				# 1. detect local peaks
				if lastswstart / batch != lastswend / batch:
					continue
				
				istart = lastswstart % batch
				iend = lastswend % batch
				locpeaks = []
				ipeak = istart
				PEAKD = 80

				print 'Detect peaks between %d and %d' % (istart, iend)

				for j in range(istart, iend):
					if j - ipeak > PEAKD:
						locpeaks.append(ipeak)
						ipeak = j

					if dat[j] > dat[ipeak]:
						ipeak = j
				
				print locpeaks
	
				# 2. calculate frequency if more thant 4 peaks
				if len(locpeaks) > 3:
					freq = (len(locpeaks) - 1) / float(locpeaks[-1] - locpeaks[0]) * 24000.0
					ncyc = freq * (lastswend - lastswstart) / 24000.0
					foswi.write('%d %f %f\n' % (lastdet, ncyc, freq))

				#	print 'Event passed'
				#else:
				#	print 'Event too short'

	# DUMPED ONCE
	# pows = [p/5000 for p in pows]
	#for i in range(batch):
	#	fop.write(struct.pack('h', dat[i]))
	#	fop.write(struct.pack('h', pows[-batch+i]))

	tshift += batch

	if detmode:
		continue

        print(len(dat))

	# to calculate mean / sd
	if len(dat) > 5 * 1000 * 1000 and mean == 0:
		mean = np.mean(pows[lrunar:])
		std  = np.std( pows[lrunar:])
		print 'Power mean / sd', mean, std
		np.savetxt(path + '.msd', np.array([mean, std]))
		
		# reset file and start detection
		detmode = True
		f.seek(0)
                if HAVEREF:
		    fr.seek(0)

                # THIS CAUSED THE BUG PREVIOUSLY - AND SHIFTED ALL TIMESTAMPS +6M
                tshift = 0

# write power
#fop = open(path + '.rpow', 'w')
#for i in range(len(pows)):
#	fop.write(struct.pack('h', pows[i]))
