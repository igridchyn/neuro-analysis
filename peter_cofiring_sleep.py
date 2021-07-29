#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import numpy as np
from sys import argv
import os

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total) + 1
    bar = fill * filledLength + '-' * (length - filledLength)
    print '\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix),
    # Print New Line on Complete
    if iteration == total: 
        print ' '

def write_corrmat(f, mat):
        for i in range(mat.shape[0]):
                for j in range(i):
                        f.write('%d %d %.4f\n' % (i, j, mat[i, j]))

# ignore swr peak !
def load_intervals(path, lab):
	f = open(path)
	ints = []
	for line in f:
		ws = line.split(' ')
		if len(ws) == 2:
			ints.append([int(w) for w in ws] + [lab])
		elif len(ws) == 3:
			ints.append([int(ws[0]), int(ws[2]), lab])		

	return ints

# non-overlapping
def merge_lists(l1, l2, ignore_overlap = True):
	i1 = 0
	i2 = 0
	mlist = []
	while i1 < len(l1) and i2 < len(l2):
		if l1[i1][0] < l2[i2][0]:
			if ignore_overlap or (l1[i1][1] < l2[i2][0]):
				mlist.append(l1[i1])
			else:
				#print 'Ignore interval because of overlap'
				pass
			i1 += 1
		else:
			mlist.append(l2[i2])
			i2 += 1
	
	# append rest of the other list
	if i1 == len(l1):
		mlist.extend(l2[i2:])
	else:
		mlist.extend(l1[i1:])

	return mlist

if len(argv) < 7:
	print 'USAGE: (1)<basename for clu/res/rem/sw files> (2)<rem population time window (ms)> (3)<sw population time window(ms)> (4)<rem correlation window> (5)<timestamps shift, samples> (6)<HSE population time window(ms)> (7)<number of spikes for fixed-spike-number correlation windows>'
	print '      if 0 time window is provided, corrseponding intervals will be ignored'
	exit(0)

base = argv[1]
wrem = int(argv[2]) * 20
wsw = int(argv[3])  * 20
tssh = int(argv[5])
whse = int(argv[6]) * 20

if len(argv) > 7:
    print 'Windows with fixed number of spikes will be used!'
    # fixed numbe of spikes windows
    FIXNS = True
    # number of pyramidal cells defining correlation window
    WINPYR = int(argv[7])

if wrem > 0:
    # load and merge all rem intervals first, then swr - merge into them ...
    print 'Load and merge rem intervals'
    intervals = load_intervals(base + 'srem', 'srem')
    rremint = load_intervals(base + 'rrem', 'rrem')
    intervals = merge_lists(intervals, rremint, True)
    nremint = load_intervals(base + 'nrem', 'nrem')
    intervals = merge_lists(intervals, nremint, True)
    print '%d rem intervals in total' % len(intervals)
    print 'First interval', intervals[0]
else:
    intervals = []

# sub-sample intervals into sub-intervals of given length and overlap
remilen = 20 * int(argv[4])
subintervals = []
overlap = remilen / 2
for inte in intervals:
	t = inte[0]
	while t + remilen < inte[1]:
		subintervals.append([t, t + remilen, inte[2]])
		t += overlap
print '%d subsampled intervals' % len(subintervals)

if wsw > 0:
    # load and merge swr intervals:
    print 'Load and merge swr intervals'
    if os.path.isfile(base + 'stsw'):
            stswints = load_intervals(base + 'stsw', 'stsw')
            subintervals = merge_lists(subintervals, stswints, False)
    else:
            print 'WARNING: no stsw file'
    if os.path.isfile(base + 'rsw'):
            rswints = load_intervals(base + 'rsw', 'rsw')
            subintervals = merge_lists(subintervals, rswints, False)
    else:
            print 'WARNING: no rsw file'
    if os.path.isfile(base + 'snsw'):
            snswints = load_intervals(base + 'snsw', 'snsw')
            subintervals = merge_lists(subintervals, snswints, False)
    else:
            print 'WARNING: no snsw file'

# append the HSE intervals
if whse > 0:
    hse_intervals = load_intervals(base + 'hse', 'hse')
    subintervals = merge_lists(subintervals, hse_intervals, False)

print '%d subsampled intervals + swrs' % len(subintervals)

clu = [int(c) for c in open(base + 'clu') if len(c) > 0]
nclu = clu[0]
clu = clu[1:]
res = [int(c) for c in open(base + 'res') if len(c) > 0]
despyr = np.loadtxt(base + 'des', dtype='str') == 'p1'

# strip session suffix
fnsuf = ''
if wsw == 0 and wrem == 0:
    fnsuf = '_hse'
    print 'Suffix _hse will be appended to the output file name'

sbase = base[:-3] if base[-3] == '_' else base[:-4]
fout = open(sbase + '.sleep_corrs' + fnsuf, 'a')
#fout = open(base + 'sleep_corrs', 'w')

ires = 0
pvec = [0] * nclu
pvecs = []
tframe = 0
# number of pyramidal cell spikes
npyr = 0

print 'Calculate correlation matrices'
os.system('setterm -cursor off')
for ii, inte in enumerate(subintervals):
	# find inteval start
	while ires < len(res) and res[ires] < inte[0]:
		ires += 1
        
        # in fixed number of spikes scenario, number of spike does not depend on window type
	wpop = wrem if 'rem' in inte[2] else (wsw if 'sw' in inte[2] else whse)
	t = inte[0]

	# collect population vectors
	while ires < len(res) and res[ires] < inte[1]:
		# current population vector : from t to t+tpop
                while ires < len(res) and ( (not FIXNS) and (res[ires] < t + wpop) or FIXNS and (npyr == WINPYR)):
			pvec[clu[ires] - 1] += 1
			ires += 1
                        npyr += int(despyr[clu[ires] - 1])

		pvecs.append(pvec)
		pvec = [0] * nclu
			
		# overlapping by 50% !
		t += wpop / 2
                if FIXNS:
                # roll back half of spike count
                    ires -= npyr / 2

		# rollback ires till population window start	
		while ires > 0 and ires < len(res) and res[ires] > t:
			ires -= 1
		ires += 1

	pmat = np.transpose(np.array(pvecs))
	mcorr = np.corrcoef(pmat)
	pvecs = []
        npyr = 0

	fout.write('%d %d %s\n' % (inte[0] + tssh, inte[1] + tssh, inte[2]))
	if isinstance(mcorr, (np.ndarray)):
		write_corrmat(fout, mcorr)

	printProgressBar(ii, len(subintervals), length=200)

os.system('setterm -cursor on')
