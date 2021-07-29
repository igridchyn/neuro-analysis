#!/usr/bin/env python3

from matplotlib import pyplot as plt
import numpy as np
from sys import argv, stdout
import os
from scipy.stats import poisson
from numpy import log, genfromtxt, sqrt
from matplotlib import animation
from tracking_processing import whl_to_speed, whl_to_pos

#========================================================================================================================================================
def prediction():	
	global time, i, last_rep
   	# construct population vector
	pop = np.zeros((ncused, 1))
	while i < len(res) and res[i] < time + WIN:
		if cmap[clu[i]-1] < 1000:
			# print clu[i],cmap[clu[i]-1]
			pop[cmap[clu[i]-1]] += 1
		i += 1

	time += WIN

	# position
	dec = np.zeros(shape)
	for c in range(0, ncused):
		# cellpred = log(poisson.pmf(pop[c], pfs[c]))
		# cellpred = pcache[c][int(pop[c])]
		#cellpred[np.isnan(cellpred)]=np.nanmin(cellpred)
		# dec += cellpred
		if pop[c] > MAXSPIKE:
			pop[c] = MAXSPIKE
		dec += pcache[c][int(pop[c])]
		# print 'Cell %d prediction - %d valid entries' % (c, sum(np.invert(np.isnan(cellpred) | np.isinf(cellpred)).flatten()))

	ind = np.invert(np.isinf(dec) | np.isnan(dec))
	if sum(ind.flatten()) > 0:
	        dec[np.invert(ind)] = min(dec[ind])
		# print '%d valid entries' % sum(ind.flatten())

	# print np.exp(dec)
	# FOR DISPLAY ONLY
	if DISPL:
		dec=np.exp(dec/DSCALE)
		dec[dec==np.min(dec)] = 0

	if sum(np.array(clsf)>=0) > 0:
		precision = sum(np.array(clsf)>0)/float(sum(np.array(clsf)>=0))
	else:
		precision = 0

	# GT / decoded positions
	amax = np.argmax(dec)

	if len(dec.shape) > 1:
		by = amax / dec.shape[1]
		bx = amax % dec.shape[1]
	else:
		bx = amax
		by = 1

	y = (by+0.5)*SBIN
	x = (bx+0.5)*SBIN

	whli = time / 480
	if whli >= len(whl):
		print('Out of range in whl')
		return dec

	bgtx = int(whl[time//480][0] / SBIN)
	bgty = int(whl[time//480][1] / SBIN)
	gtx = whl[time//480][0]
	gty = whl[time//480][1]

	middle = dec.shape[1]//2 if len(dec.shape) > 1 else dec.shape[0] // 2
	BINBORD = 200 // SBIN

	# environment classification test
	spd = speed[time//480]
	if spd < SPDTHOLD or CV and not istestwhlt(whli):
		clsf.append(-1)
	else:
		clsf.append(int((bgtx-BINBORD)*(bx-BINBORD) >= 0))
		errors.append(sqrt((x-gtx)**2 + (y-gty)**2))
		if len(dec.shape) > 1:
			conf = np.max(dec[:,0:middle]) - np.max(dec[:,middle:])
		else:
			conf = np.max(dec[0:middle]) - np.max(dec[middle:])
		if conf < 0:
			conf = - conf
		#conf = log(conf)
		confidences.append(conf)

	# report
	if time > last_rep + REP_INT:
#		try:
		confvserr = np.corrcoef(np.array(confidences), np.array(errors))[1,0]
		stdout.write('Time = %d, speed = %6.2f, total classification precision=%.2f, median error=%5.2f, corr of error with confidence = %3.2f\r' % (time, speed[time//480], precision, np.median(errors), confvserr))
		last_rep += REP_INT
#		except:
#		print('Error during report attempt')

	return dec
#========================================================================================================================================================
def update_display(*args):
	dec = prediction()

	# set max to red (max)
	amax = np.argmax(dec)
	by = amax//dec.shape[1]
	bx = amax%dec.shape[1]
	
	dec[by, bx]=1

	dec /= np.nanmax(dec)

	# set real pos to blue (min)
	#print len(whl), time/480
	gtx = int(whl[time//480][0] / SBIN)
	gty = int(whl[time//480][1] / SBIN)

	#if gtx < 70:
	dec[gty,gtx] = 0

	im.set_array(dec)

	return im,
# ====================================================================================================================================================================
def istestwhlt(whlt):
    whlt = int(round(whlt))

    if not CV:
        return true

    # odd / even 100 ms window (50 Hz tracking -> // 5 = number of 100 ms window
    return not bool((whlt // 5) % 2)
# ====================================================================================================================================================================

if len(argv) < 7:
	print('Usage: ' + argv[0] + ' (1)<path base of pfs/> (2)<path to dir with clu/res> (3)<path to whl> (4)<session> (5)<speed thold> (6)<minimal peak firing rate> (7)<file with swr timestamps>')
	print('Decode using pfs dumped by LFPO-spike_display / python script')
	exit(0)

CV = False
# was hard-coded 4 before
#SPDTHOLD = 4
SPDTHOLD = float(argv[5])
PFRTHOLD = float(argv[6])

#pfpref = argv[1] + 'pfs/pf_'
pfpref = argv[1]
res_name = argv[2] + 'res'
clu_name = argv[2] + 'clu'
session = argv[4]
whl = whl_to_pos(open(argv[3]), True)
speed = whl_to_speed(whl)

res = [int(r) for r in open(res_name).read().split('\n') if len(r) > 0]
clu = [int(r) for r in open(clu_name).read().split('\n') if len(r) > 0]
NCELL = max(clu)
print('Number of cells = %d' % NCELL)
# position sampling rate multiplied by window size
# position sampling rate already accounted in the rate maps!
POSSR = 0.1

pfs = []

cmap = [1000] * NCELL
ncused = 0

for c in range(1, NCELL + 1):
	pfpath = pfpref + str(c) + '_' + session + '.mat'
	#pfpath = pfpref + str(c) + '.mat'
	if not os.path.isfile(pfpath):
		print('No PF for cluster ', c)
		continue

	
	pf = genfromtxt(pfpath)[:,:]
	pf *= POSSR

        # DEBUG: BEWARE OF X/Y ORDER
        # pf = pf.transpose()

	# because dumped pf is in spikes / 0.02 s
	peakfr = np.nanmax(pf[np.invert(np.isinf(pf))]) * 10 # * 50, * 10 because before it was multiplied by window size
	print('Peak firing rate of cell %d = %.2f' %(c, peakfr))
	if peakfr < PFRTHOLD:
		continue

	cmap[c-1] = ncused
	ncused += 1

	pf[np.isinf(pf)] = np.nan
	pfs.append(np.array(pf))

	pfinf = sum(np.isinf(pf).flatten())
	pfnan = sum(np.isnan(pf).flatten())
	print('%d nan, %d inf (%d in total)' % (pfinf, pfnan, pfinf+pfnan))

#	plt.imshow(pf)
#	plt.title('Cell %d' % c)
#	plt.colorbar()
#	plt.show()

#exit(0)

shape = pfs[0].shape
print('PF shape: ', shape)

# cache log-probs for each cell and each number of spikes
MAXSPIKE = 30
pcache = []
for c in range(0, ncused):
	pcache.append([])
	for n in range(0, MAXSPIKE + 1):
		pcache[c].append(poisson.logpmf(n, pfs[c]))
		pcache[c][n][np.isnan(pcache[c][n])] = np.nanmin(pcache[c][n])

# decoding
i = 0
time = res[0]
WIN = 2400
# exponential display scale
DSCALE = 10 # 100 / 20
SBIN = 6
PRED_DELAY = 24000 #7811000
PRED_END = 43200000
# reporting interval
REP_INT = 100000
last_rep = 0
#DISPL = True
DISPL = False


# skip
while i < len(res) and res[i] < PRED_DELAY:
	i += 1

if i == len(res):
	print('ERROR: delay larger than input duration!')
	exit(1)

time = (res[i] // WIN) * WIN

print('%d cells will be used' % ncused)

# 1-correct, 0-wrong, -1 - speed-filtered
clsf = [] 
errors = []
confidences = []




# without display
if not DISPL and len(argv) <= 7:
	while i < len(res) and res[i] < PRED_END:
		prediction()

# predict from swrs
if len(argv) > 7:
	swrs = [int(s) for s in open(argv[7]) if len(s)>0]
	NSPIKES = 100
	sc = 0
	pred_dump = 'bay_swr_dec/'
	if not os.path.isdir(pred_dump):
		os.mkdir(pred_dump)
	for swr in swrs:
		time = swr - 480
		# set to first spike in swr
		while i < len(res) and res[i] < time:
			i += 1
		WIN = (res[i+NSPIKES] - res[i]) if i+NSPIKES < len(res) else (res[-1]-res[i])
		dec = prediction()
		np.savetxt(pred_dump + 'bay_swr_dec_%d.mat' % sc, dec[0:dec.shape[0]/2, :].transpose())
		sc += 1
	exit(0)

#outdir = argv[1] + 'bay_out_' + argv[4] + '_' + str(PRED_DELAY) + '_' + str(PRED_END) +'/'
outdir = os.path.dirname(argv[1]) + '/bay_out_' + argv[4] + '_' + str(PRED_DELAY) + '_' + str(PRED_END) +'/'
if os.path.isdir(outdir):
    print('WARNING: Output directory exists, delete first')
    #exit(1)
else:
    os.mkdir(outdir)

fconf = open(outdir + 'confidences.txt', 'w')
for conf in confidences:
	fconf.write('%f\n' % conf)
fclsf = open(outdir + 'clsf.txt', 'w')
for cl in clsf:
	fclsf.write('%d\n' % cl)
ferrors = open(outdir + 'errors.txt', 'w')
for error in errors:
	ferrors.write('%d\n' % error)


# with display
if DISPL:
	fig = plt.figure()
	im = plt.imshow(np.zeros(shape), animated = True, vmin = 0, vmax=1, interpolation = 'none')
	ani = animation.FuncAnimation(fig, update_display, interval=50, blit=True)
	plt.show()

print('\nOVER')
