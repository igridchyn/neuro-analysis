#!/usr/bin/env python2

# parsing out strings like 
# 'LPT Trigger: STOP INHIBITION at 779106'

from sys import argv
import os

if len(argv) < 6:
	print argv[0], ' (1)<path to file with timestamps> (2)<shift in timespamps> (3)<confidence threshold> (4)<output file 1 - inhibited> (5)<output file 2 - not inhibited>'
	print 'Parse out timestamps with given confidence criteron'
	exit(0)

print 'WARNING: synchrony timestamps will be written for both DON"T INHIBIT and INHIBIT cases'

file = open(argv[1])
cthold = float(argv[3])

shift = 0
if len(argv) > 2:
	shift = int(argv[2]) + 720
        print 'WARNING: time shift + 360'

if os.path.isfile(argv[4]):
    print 'ERROR: output file exists'
    exit(1)
#timestamps = open(argv[4], 'w')
#timestamps_2 = open(argv[5], 'w')
fsyncs = open(argv[4], 'w')
swrt = 0

nextc = False
lastswrt = -1
for line in file:
	# print line

	#LPT Trigger: Synchrony detected at 2195070
	if 'Synchrony' in line and 'ARRAY' not in line:
		try:
			swrt = str(int(line.split(' ')[-1]) + shift) + '\n'
			swrts = swrt
                        fsyncs.write(swrt)
			# timestamps.write(swrt)
		except:
			print 'Error parsing line:', line

	if nextc:
		conf = float(line.split(' ')[-1])

		if swrt > lastswrt and conf > cthold:
                        pass
			# was swrts
			#timestamps.write(str(swrt) + '\n')
			#timestamps.write(str(ttimeout) + '\n')

		lastswrt = swrt
		nextc = False

	if 'TIMEOUT' in line:
		ttimeout = int(line.split(' ')[-1])

	if 'start INHIBITION' in line or 'decision: INHIBIT, start' in line:
	#if 'window center' in line:
		swrt = int(line.split(' ')[-1]) + shift
		# swrts = str(swrt) + '\n'
		nextc = True

	#if 'STOP' in line:
	#	#print line

	if "decision: DON'T INHIBIT, start" in line:
		swrt = str( int(line.split(' ')[-1]) + shift) + '\n'
		#timestamps_2.write(swrt)
		#timestamps_2.write(str(ttimeout + shift) + '\n')
		#timestamps_2.write(swrts)

