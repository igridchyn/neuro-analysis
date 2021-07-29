#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from iutils import *
from tracking_processing import *
from scipy.ndimage.filters import gaussian_filter1d as gf1d
from call_log import *
#import pickle
import cPickle as pickle

def place_field_centers(whl, speed, clu, res):
	pf_centers = []
	# calculate linear rate maps, do weighted average
	bs = 2
	STHOLD = 4
	NBIN = 200
	OCCTHOLD = 3

	spk = np.zeros((NCELL, NBIN))
	occ = np.zeros((NBIN, 1))

	TSTART = res[-1] / 2
	
	# occupancy
	for wi in range(len(whl)):
		if speed[wi] < STHOLD or wi * 480 < TSTART:
			continue
		xb = int(round(whl[wi][0] / bs))
		occ[xb] += 1

	# count spikes
	for ri in range(len(res)):
		t = res[ri] / 480

		
		if t >= len(speed):
			continue
		if  speed[t] < STHOLD or wi * 480 < TSTART:
			continue

		xb = int(round(whl[t][0] / bs))
		spk[clu[ri]-1, xb] += 1 

	occ[occ < OCCTHOLD] = 0

	# divide by occupancy
	for b in range(NBIN):
		if occ[b] > 0:
			spk[:,b] /= occ[b]

	# smooth
	for c in range(NCELL):
		spk[c, :] = gf1d(spk[c, :], 5)

	mx = np.max(spk)

	pfcs1 = []
	pfcs2 = []
	# find place field centers - weighted average
	for c in range(NCELL):
		sm1 = np.sum(spk[c, :100])
		sm2 = np.sum(spk[c, 100:])
		
		ws1 = 0
		for b in range(NBIN/2):
			ws1 += b * spk[c, b]
		ws2 = 0
		for b in range(NBIN/2, NBIN):
			ws2 += b * spk[c, b]

		if sm1 > 0:
			pfc1 = int(round(ws1 / sm1))
			spk[c, pfc1] = mx
		else:
			pfc1 = 0

		if sm2 > 0:
			pfc2 = int(round(ws2 / sm2))
			spk[c, pfc2] = mx
		else:
			pfc2 = NBIN/2
	
		pfcs1.append(pfc1)
		pfcs2.append(pfc2)

	print np.argsort(pfcs1)

	# DEBUG
	#plt.imshow(spk[:,:], interpolation = 'none')
	#plt.show()

	return np.argsort(pfcs1), np.argsort(pfcs2)

def raster(event_times_list, esplit, actresp, **kwargs):
    """
    Creates a raster plot
    Parameters
    ----------
    event_times_list : iterable
                       a list of event time iterables
    color : string
            color of vlines
    Returns
    -------
    ax : an axis containing the raster plot
    """

    # SWAP
    if e1targ:
        event_times_list = event_times_list[esplit:] + event_times_list[:esplit]
	actresp = actresp[esplit:] + actresp[:esplit]
	esplit = len(actresp) - esplit

    ax = plt.gca()
    for ith, trial in enumerate(event_times_list):
        plt.vlines(trial, ith + .5, ith + 1.5, linewidth=2,**kwargs)
    #plt.ylim(.5, len(event_times_list) + .5)

    talph = 0.3
    plt.text(2200, esplit / 2, 'CONTROL', alpha = talph)
    plt.text(2200, esplit + (len(actresp) - esplit) / 2, 'TARGET', alpha = talph)

    if SLEEP:
	    plt.axvline(AWIN)
	    plt.axvline(AWIN + 2400, color = 'red')
    plt.axhline(len(event_times_list)+0.5)

    plt.axhline(esplit+0.5)

    # plot rectangles designating inhibited, disinhibited and unaffected cells
    # E1 disinh
    ri = 0
    while actresp[ri] <= 0:
	ri += 1 

    print actresp	

    ral = 0.1 if SLEEP else 0.1
    fcolred = (1.0, 0, 0, ral)
    wstart = AWIN if SLEEP else 0
    #wlen = 2400 if SLEEP else (IEND - ISTART)
    wlen = 6000 if SLEEP else (IEND - ISTART)

    icol = 'black'

    plt.ylim([0.5, len(event_times_list) - 0.5])
    if not SLEEP:
        plt.xlim([0, (IEND-ISTART)])

    #if 'ninh' not in tspath and not NINH:
    if True:
	    #r1i = patches.Rectangle((wstart, 0.5), wlen, ri, linewidth=1, facecolor=icol, edgecolor='none', alpha=ral)
	    r1i = patches.Rectangle((0, 0.5), wlen, ri, linewidth=1, facecolor=icol, edgecolor='none', alpha=ral)
	    ax.add_patch(r1i)

	    ris = ri
	    while actresp[ri] >= 0:
		ri += 1
	    #r1d = patches.Rectangle((wstart, ris+0.5), wlen, ri-ris, linewidth=1, facecolor='red', edgecolor='none', alpha=ral)
	    #ax.add_patch(r1d)

	    ris = ri
	    while actresp[ri] <= 0:
		ri += 1
	    #r2i = patches.Rectangle((wstart, ris+0.5), wlen, ri-ris, linewidth=1, facecolor=icol, edgecolor='none', alpha=ral)
	    r2i = patches.Rectangle((0, ris+0.5), wlen, ri-ris, linewidth=1, facecolor=icol, edgecolor='none', alpha=ral)
	    ax.add_patch(r2i)

	    ris = ri
	    while ri < len(actresp) and actresp[ri] >= 0:
		ri += 1
	    #r2d = patches.Rectangle((wstart, ris+0.5), wlen, ri-ris, linewidth=1, facecolor='red', edgecolor='none', alpha=ral)
	    #ax.add_patch(r2d)

	    # print r1i, r1d, r2i, r2d
	#print r1i, r2i

    if  not NINH:
	# on the whole inhibition area
            r1i = patches.Rectangle((wstart, 0.5), wlen, 1000, linewidth=1, facecolor=icol, edgecolor='none', alpha=ral)
	    ax.add_patch(r1i)

    return ax

def filter(pfspath, MINPFR, MAXPFR, MAXSP, MINCOH):
	sp1 = read_float_array('../sparsity_BS6_OT5_E1.txt')
	sp2 = read_float_array('../sparsity_BS6_OT5_E2.txt')
	coh1 = read_float_array('../coherence_BS6_OT5_E1.txt')
	coh2 = read_float_array('../coherence_BS6_OT5_E2.txt')
	pfrs1 = []
	pfrs2 = []
	print 'WARNING: using mean rates instead of peak rates'
	for line in open(pfspath):
		ws = line.split(' ')
		# peak rates in env 1-2 in the 2nd session of the PFS file
		pfrs1.append(float(ws[10]))
		pfrs2.append(float(ws[11]))
		
		#pfrs1.append(float(ws[3]))
		#pfrs2.append(float(ws[4]))
	pfrs1 = np.array(pfrs1)
	pfrs2 = np.array(pfrs2)
	# sparsity, coherence, rate

	# 0.3, 0.5
	#MAXSP = 1.0
	#MINCOH = 0.0

	# DOF ??? make two separate ones - will have fewer cells though - but nicer waking rasters ?
	# otherwise sets can overlap if SELF < 1
	filt_scr = ((sp1 < MAXSP) & (coh1 > MINCOH) & (pfrs1 > MINPFR) & (pfrs1 < MAXPFR)) | ((sp2 < MAXSP) & (coh2 > MINCOH) & (pfrs2 > MINPFR) & (pfrs2 < MAXPFR))

	# selective to 1st, 2nd
	return filt_scr & (np.isnan(pfrs2) | (pfrs1 > SELF * pfrs2) ), filt_scr & (np.isnan(pfrs1) | (pfrs2 > SELF * pfrs1))


NARG = 5

if len(argv) < NARG:
	print 'USAGE: (1)<base name for whl/clu/res> (2)<int start> (3)<int end> (4)<sleep mode : 0/1> [-o <order file> -e <0/1 - order envirionment> -a <timestamp - around> -sel <selectivity filter>] -tf <timestamps file> -awin <around window> -skip <number of events in the file to skip>'
	print 'Build raster plot of a given session in the given interval'
	exit(0)

suppress_warnings()

argv = resolve_vars(argv)
[animal, day] = resolve_vars(['%{animal}', '%{day}'])
ld = log_call(argv)

# options dictionary
od = parse_optional_params(argv[NARG:])

ISTART = int(argv[2])
IEND   = int(argv[3])

AWIN = gdvi(od, 'awin', 2400)

ar = gdvi(od, 'a', 0)
if ar > 0:
	print 'Override intrval - use 50 ms around %d' % ar
	ISTART = ar - AWIN
	IEND   = ar + AWIN

fresp = gdv(od, 'resp', '')
responses = read_float_array(fresp)

base = argv[1]
clu = [int(c) for c in open(base + 'clu')]
res = [int(c) for c in open(base + 'res')]
NCELL = max(clu)

# find cell's place field center (linear) to order them accordingly

SELF = gdvf(od, 'sel', '')
minpfr = gdvf(od, 'minpfr')
maxpfr = gdvf(od, 'maxpfr')
maxsp = gdvf(od, 'maxsp')
mincoh = gdvf(od, 'mincoh')
# cellsf1, cellsf2 = filter('../PFS_1_2_FTS_2.out')
cellsf1, cellsf2 = filter('../PFS_1_2_FTS_1_OCC-5_PART-1.out', minpfr, maxpfr, maxsp, mincoh)

print 'Filter passing cells (s, c, rates, sel): %d / %d' % (np.sum(cellsf1), np.sum(cellsf2))

#SLEEP = False
#SLEEP = True
SLEEP = bool(int(argv[4]))

# read signal snippets file
spath = gdv(od, 's', '')
if True: #SLEEP:
	if spath == '':
		SIGNAL = False
		#print 'ERROR: no signal file provided'
		#exit(1)
	else:
		SIGNAL = True
		if os.path.isfile(spath + '.sd'):
			fsb = open(spath + '.sd', 'rb')
			dicsig = pickle.load(fsb)
			print 'WARNING: using dump of .sig'
		else:
			fs = open(spath)
			dicsig = {}
			while True:
				l = fs.readline()
				if len(l) == 0:
					break
				off = int(l)
				sig = [int(s) for s in fs.readline().split(' ')[:-1]]
				dicsig[off] = sig
			fsb = open(spath + '.sd', 'wb')
			pickle.dump(dicsig, fsb, pickle.HIGHEST_PROTOCOL)
			
		print len(dicsig), ' signal snippets'

opath = gdv(od, 'o', '')
if opath == '':
	whl = whl_to_pos(open('../9l/' + base.replace('13ssi', '9l') + 'whl.linear'), False)
	speed = whl_to_speed(whl)
	pfc1, pfc2 = place_field_centers(whl, speed, clu, res)
	print 'Calculated place field centers...'
else:
	print 'Read order list from file ...'
	pfc1 = read_int_list(opath + 'pfo1')
	pfc2 = read_int_list(opath + 'pfo2')
	
# save both - e.g. to be used in SWR rasters
write_array(pfc1, base + 'pfo1')
write_array(pfc2, base + 'pfo2')

# deprecated - now both are used and combined
#pfc = [pfc1, pfc2][gdvi(od, 'e', 0)]

SKIP = gdvi(od, 'skip', 0)

#if '0430' in base:
#	ISTART += 25000
#	print 'WARNING: ISTART + 25k for 0430'
intervals = [[ISTART, IEND]]

tspath = gdv(od, 'tf', '')
if tspath != '':
	intervals = []
	tss = read_int_list(tspath)
	for ts in tss[SKIP:]:
		intervals.append([ts - AWIN, ts + AWIN])

respord = np.argsort(responses)
# print responses, respord
resp_nounaff = []
rinh = gdvf(od, 'rinh')
rdinh = gdvf(od, 'rdinh')
for r in respord:
	if responses[r] < rinh or responses[r] > rdinh:
		resp_nounaff.append(r)
respord = resp_nounaff

print 'Filtered out reponsive cells: %d out of %d' % (len(respord), len(responses))

#print 'Intervals: ', intervals

e1targ = not bool(int(gdv(od, 'targ')))

# reversed res, for faster indexing:
ires = {}
for i in range(len(res)):
	ires[res[i]] = i	

NINH = 'NINH' in spath
TMIN = 1500

for ii, interval in enumerate(intervals):

	print ii + SKIP

	# per cell, relative to start
	spike_times = []

	#RSTART = 0
	#while RSTART < len(res) and res[RSTART] < interval[0]:
	#	RSTART += 1

	#find through inversed res:
	key = interval[0]
	while key not in ires:
		key += 1
	RSTART = ires[key]

	# actual reponses - for cells plotted
	actresp = []

	# form sorlist with 2 groups within: first inh, then dinh
	pfc1_r = []
	for c in pfc1:
		if responses[c] < 0 and c in respord:
			pfc1_r.append(c)
	for c in pfc1:
		if responses[c] > 0 and c in respord:
			pfc1_r.append(c)
	pfc2_r = []
	for c in pfc2:
		if responses[c] < 0 and c in respord:
			pfc2_r.append(c)
	for c in pfc2:
		if responses[c] > 0 and c in respord:
			pfc2_r.append(c)
	
	# selective to 1st environment, ordered by their place field in the 1st environment
	sortar = respord if SLEEP else pfc1_r
	#for c in pfc1:
	#for c in respord:
	for c in sortar:
		if not cellsf1[c] or c not in respord:
			continue

		i = RSTART
		cellspikes = []
		while res[i] < interval[1]:
			if clu[i]-1 == c:
				cellspikes.append(res[i]-interval[0])
			i += 1
		spike_times.append(cellspikes)
		actresp.append(responses[c])

	split = len(spike_times)

	#cellsp = np.array([len([a for a in l if a < 3600 and a > 1500]) for l in spike_times])
	cellsp = np.array([len([a for a in l if a < 3600 and a > TMIN]) for l in spike_times])
	cellsp_light = np.array([len([a for a in l if a < 5000 and a > 3600]) for l in spike_times])
	e1n = sum(cellsp)
	e1n_light = sum(cellsp_light)
	ncell_e1 = len(spike_times)
	n_act_e1 = np.sum(cellsp > 0)

	# selective from 2nd environment, ordered by their place field in the 2nd environment
	sortar = respord if SLEEP else pfc2_r
	#for c in pfc2:
	#for c in respord:
	for c in sortar:
		if not cellsf2[c] or c not in respord:
			continue

		i = RSTART
		cellspikes = []
		while res[i] < interval[1]:
			if clu[i]-1 == c:
				cellspikes.append(res[i]-interval[0])
			i += 1
		spike_times.append(cellspikes)
		actresp.append(responses[c])

	#cellsp = np.array([len([a for a in l if a < 3600 and a > 1500]) for l in spike_times])
	cellsp = np.array([len([a for a in l if a < 3600 and a > TMIN]) for l in spike_times])
	cellsp_light = np.array([len([a for a in l if a < 5400 and a > 3600]) for l in spike_times])
	#e2n = sum([len([a for a in l if a < 3600]) for l in spike_times]) - e1n
	e2n = sum(cellsp) - e1n
	e2n_light = sum(cellsp_light) - e1n_light
	ncell_e2 = len(spike_times) - ncell_e1
	n_act_e2 = np.sum(cellsp > 0) - n_act_e1

	print 'Number of spikes per environment: %d / %d' % (e1n, e2n) 

	# actual ratio of filtered cells per environment
	ncellrat = ncell_e2 / float(ncell_e1)
	# minimal required ratio of spikes
	MINRAT = 4
	if SLEEP and ((e1n > 0 and e2n/float(e1n) / ncellrat < MINRAT) and (e2n > 0 and (e1n/float(e2n) * ncellrat < MINRAT))):# or (e1n + e2n < 7)):
		#print 'Skip... : small spike number ratio OR few total spikes'
		print 'Skip... : small spike number ratio'
		continue

	if SLEEP and ((e1n > e2n) != e1targ) != NINH:
		print 'SKIP: WRONG ENVIRONMENT DOMINATES ...'
		continue

	# check that inhibited cells spike less:
	fail = False
	# number of active inhibited cells
	INHACT  = 0
	DINHACT = 0
	for c in range(len(actresp)):
		star = np.array(spike_times[c])
		bef_sum = np.sum((star < 3600) & (star > TMIN))
		aft_sum = np.sum((star > 3600) & (star < 6000))

		if bef_sum > 0:
			if actresp[c] < 0:
				INHACT += 1
			else:
				DINHACT += 1

		if actresp[c] > 0:
			continue

		# relaxed version allows 1-2 spikes after ...
		if SLEEP and (aft_sum >= bef_sum) and not NINH and (aft_sum > 1):
			print 'SKIP: SOME OF THE INHIBITED CELLS SPIKE GEQ in 100 ms after light than before', c
			fail = True
			break
	if fail:
		continue

	# i/di; Jozsef : 3/4; relaxed: 2/3
	MININHACT =  3
	MINDINHACT = 4
	if NINH:
		if INHACT + DINHACT < 5:
			print 'SKIP: <5 active cells (inh + dinh)'
	else:
		if SLEEP and INHACT < MININHACT:
			print 'SKIP: <%d active inhibited cells before!' % MININHACT
			continue
		if SLEEP and DINHACT < MINDINHACT:
			print 'SKIP: <%d active disinhibited cells before!' % MINDINHACT
			continue

	# check if present in good signals ...
	if SIGNAL and interval[0] + AWIN not in dicsig:
		print 'WARNING:', interval[0] + AWIN, 'Not found in signals'
		# figure out later
		#continue

	MINACT = 5
	if SLEEP and n_act_e1 < MINACT and n_act_e2 < MINACT:
		print 'Skip : few active cells'
		continue

	MIN_N_LIGHT = 8
	if SLEEP and not NINH and (e1n_light < MIN_N_LIGHT or e2n_light < MIN_N_LIGHT):
		print 'SKIP: few spikes in one of the environments during the light: <', MIN_N_LIGHT
		continue

	ddpi = 100.0
	plt.figure(figsize = (800.0/ddpi, 520.0/ddpi), dpi=ddpi)

	ax = raster(spike_times, split, actresp)

	if SIGNAL:
		if interval[0] + AWIN in dicsig:
			print 'PLOT SIGNAL'
			DIV = 1000 if SLEEP else 5
			strans = np.array([float(s) / DIV for s in dicsig[interval[0] + AWIN]])
		else:
			strans = np.array([0, 0])
		# strans = strans - np.min(strans) + len(spike_times)
		strans = strans + 10 + len(spike_times)
		sr = 300
		ax.plot(range(1,len(strans), sr), strans[0::sr], color = 'black')
		#plt.ylim(0.5, max(strans))
		plt.ylim(0.5, len(spike_times) + 19)

	# plot rectangles over the inhibition area + over inhibited and disinhibited cells

	if SLEEP:	
		plt.xlim([1500, 6000])
	#else:
	#        plt.xlim([18000, plt.gca().get_xlim()[1]])

	# plt.title('%s - %s - %d' % (animal, day, ii))

	set_xticks_off()
	set_yticks_off()
	set_ticks_off()
	plt.yticks([],[])

	plt.tight_layout()

	if not SLEEP:
		plt.savefig('/home/igor/resim/_AUTOSAVE/RASTER_WAKING_%s%s.png' % (argv[1], argv[2]))
	else:
		plt.savefig('/home/igor/resim/_AUTOSAVE/RASTER_SLEEP_%s_%s%d.png' % (('NINH' if NINH else 'INH'), argv[1], ii + SKIP))
	plt.show()
	plt.close()
