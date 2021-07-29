#!/usr/bin/env python
import os
import shutil
from sys import argv

a1 = 'jc181'
a2 = 'jc182'
a3 = 'jc184'
a4 = 'jc188'

days = [[a1, '1124'],
[a1, '1125'],
[a1, '1127'],
[a1, '1130'],
[a2, '0106'],
[a2, '0107'],
[a2, '0109'],
[a2, '0112'],
[a3, '0226'],
[a3, '0227'],
[a3, '0228'],
[a3, '0301'],
[a3, '0304'],
[a4, '0428'],
[a4, '0429'],
[a4, '0430'],
[a4, '0501'],
[a4, '0502'],
[a4, '0503'],
]

# 1. run model build 
# 2. run deocding on self\
# 3. run decoding error analysis
# move output 
# 4. run deocding on post-l 1st half
# 5. run decoding error analysis
# move output

def run_for_day(animal, day):
	# read env border from the day config
	fdc = open('../Res/day/d_%s_%s.conf' % (animal, day))
	found = False
	for line in fdc:
		if line.startswith('nbinsx'):
			found = True
			middle = int(line.split('=')[-1])
	if not found:
		print 'ERROR: could not find nbinsx in day config!'
		exit(124345)

	msession = '9l'
	pl_session = '16l'
	pl_dump_end_session = '1'
	if animal=='jc181' or animal=='jc182' and day=='0106':
		msession = '10l'
	if animal=='jc182' and day=='0106':
		pl_session = '17f'
		pl_dump_end_session = '3'

	# os.system('./lfp_online ../Res/EXPERIMENTAL_build_model.conf animal=%s day=%s session=%s nbinsx=90 nbinsy=50' % (animal, day, msession))
	os.system('./lfp_online ../Res/EXPERIMENTAL_decoding_online.conf animal=%s day=%s kd.interleaving.windows=1 kd.dump.end=3 kd.prediction.delay=1 session=%s session_model=%s nbinsx=90 nbinsy=50' % (animal, day, msession, msession))
	# os.system('python ../decoding_error.py dec_bay.txt %s 1 %s 0 2' % (middle, middle))
	os.system('python ../decoding_error.py dec_bay.txt 90 50 180 0 4')
	shutil.copy('decerr.out', 'decer_%s_%s_%s_LIL.out' % (animal, day, msession))
	os.system('./lfp_online ../Res/EXPERIMENTAL_decoding_online.conf animal=%s day=%s kd.interleaving.windows=0 kd.dump.end=%s kd.prediction.delay=24000 session=%s session_model=%s nbinsx=90 nbinsy=50' % (animal, day, pl_dump_end_session, pl_session, msession))
	# os.system('python ../decoding_error.py dec_bay.txt %s 1 %s 0 2' % (middle, middle))
	os.system('python ../decoding_error.py dec_bay.txt 90 50 180 0 4')
	shutil.copy('decerr.out', 'decer_%s_%s_%s_PL.out' % (animal, day, msession))

	print 'Used nbinsx =', middle

if len(argv) == 3:
	animal = argv[1]
	day = argv[2]
	msession = argv[3]
	exit(0)

if len(argv) != 2 or argv[1] != 'all':	
	print 'USAGE: (1)<animal> (2)<day>'
	print 'or (1)<all> to run for all days'
	exit(0)

# run for all days
for d in days:
	run_for_day(d[0], d[1])
