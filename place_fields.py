#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
#from iutils import *
#from call_log import *
from tracking_processing import *
from imath import gaussian
from scipy import ndimage as nd
#from astropy.convolution import Gaussian2DKernel, convolve
import astropy.convolution as apc
import random
#from iutils_p3 import *

# generate place fields from whl and clu

def choices(l, n):
    return [random.sample(l, 1)[0] for i in range(n)]

def ri(f):
    return int(np.round(f))

def kernel(size, sigma):
    k = np.zeros((size, size))

    assert size % 2 == 1

    h = size//2
    sm = 0
    for x in range(-h, h+1):
        for y in range(-h, h+1):
            gval =np.exp(-(((x)**2 + (y)**2) / sigma))
            k[x+h,y+h] = gval
            sm += gval

    k /= sm

    return k

def istrainwhlt(whlt):
    whlt = int(round(whlt))

    if not CV:
        return True

    # odd / even 100 ms window (50 Hz tracking -> // 5 = number of 100 ms window
    return bool((whlt // 5) % 2)

if len(argv) < 8:
	print('USAGE: (1)<base for clu/res> (2)<base for whl> (3)<bin size> (4)<smoothing sigma> (5)<speed filt> (6)<occupancy threshold> (7)<base for the output> (8-N)<additional bases>')
	print('BUILD PLACE FIELDS?')
	exit(0)

# ld = log_call(argv)

#argv = resolve_vars(argv)

BASE = argv[1]
WBASE = argv[2]
BIN = float(argv[3])
SX = float(argv[4])
ST = float(argv[5])
OT = float(argv[6])
OUTBASE = argv[7]
# for Jozsef's pipeline
#WHLSR = 512
WHLSR = 480

PLT = False
# use cross-validation: odd 100ms windows for learning and even for testing
CV = False

OCCPATH = OUTBASE + 'occ_0.mat'
if os.path.isfile(OCCPATH):
    print('WARNING: Occupancy file exists in th target dir, delete first!')
    # exit(1)

if not os.path.isdir(os.path.dirname(OUTBASE)):
    os.makedirs(os.path.dirname(OUTBASE))

if os.path.isfile(OUTBASE + 'params.txt'):
    print('WARNING: Params file exists, delete first')
    #exit(1)
fpar = open(OUTBASE + 'params.txt', 'w')
fpar.write('BIN SIZE = %s\nSMOOTHING SIGMA = %s\nSPEED FILTER = %s\nOCCUPANCY THRESHOLD = %s\n' % (argv[3], argv[4], argv[5], argv[6]))

# read sessions and groups
#f = open('sessions_groups.txt')
#sessions = [int(t) for t in f.readline().split()]
#groups = [int(t) for t in f.readline().split()]

sessions = []
groups = [0]

clu = [int(c) for c in np.loadtxt(BASE + 'clu')]
clu = clu[1:]
res = [int(r) for r in np.loadtxt(BASE + 'res')]
whl = whl_to_pos(open(WBASE + 'whl'), True)
WHL_SCALE = 0.875
for i in range(1, len(whl)):
	if whl[i][0] < 1000:
		whl[i][0] *= WHL_SCALE
		whl[i][1] *= WHL_SCALE

# FOR JOZSEF'S WHL
#whl = np.loadtxt(WBASE + 'whl')
# fill gaps:
#for i in range(1, len(whl)):
#	if whl[i][0] < 0:
#		whl[i] = whl[i-1]

for BASE2 in argv[8:]:
    # shift from previous
    rshift = len(whl) * WHLSR
    clu.extend([int(c) for c in np.loadtxt(BASE2 + 'clu')])
    res.extend([int(r) + rshift for r in np.loadtxt(BASE2 + 'res')])
    whlt = whl_to_pos(open(BASE2 + 'whl'), True)
    whl.extend(whlt)

whl = np.array(whl)
speed = whl_to_speed(whl)

# IGNORE VALUES WITH Y > 0
YMAX = 500
for i in range(1, len(whl)):
    if whl[i,1] > YMAX:
        whl[i,:] = whl[i-1,:]
        print('WARNING: WHL ENTRY WITH Y > 300 IGNORED')

# DEBUG: speed hist
#plt.hist(speed, np.arange(0, 40, 0.5))
#plt.show()
#exit()

nclu = int(max(clu) + 1)
# alias
ncell = nclu
#nbinx = ri(max(whl[:,0] / BIN)) + 1
#nbiny = ri(max(whl[:,1] / BIN)) + 1
nbinx = 35
nbiny = 35

# build occupancy map
occmaps = [ np.zeros((nbinx, nbiny)) for i in range(max(groups) + 1)]
# add value proportional to the value of gaussian in the center - to the bin and 8 bins around
ises = 0
for wi in range(len(whl)):
    wbx = ri(whl[wi, 0] / BIN)
    wby = ri(whl[wi, 1] / BIN)

    if speed[wi] < ST or not istrainwhlt(wi) or wbx < 0:
        continue
    
    # check if next session border reached
    tres = wi * WHLSR
    if ises < len(sessions) and tres > sessions[ises]:
        ises += 1

    gsum = 0
    gvals = np.zeros((3,3))
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if wbx + dx < 0 or wbx + dx >= nbinx or wby + dy < 0 or wby + dy >= nbiny:
                continue
            # !!! GAUSSIAN WITH SIGMA = BIN WIDTH !!!
            gval =  np.exp((-(wbx + dx + 0.5 - whl[wi,0]/BIN)**2 - (wby + dy + 0.5 - whl[wi,1]/BIN)**2))
            gvals[dx+1,dy+1]=gval
            # occmap[wbx + dx, wby + dy] == gval
            gsum += gval 

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if wbx + dx < 0 or wbx + dx >= nbinx or wby + dy < 0 or wby + dy >= nbiny:
                continue

            #gval =  np.exp((-(wbx + dx + 0.5 - whl[wi,0]/BIN)**2 - (wby + dy + 0.5 - whl[wi,1]/BIN)**2)/SX)
            occmaps[groups[ises]][wbx + dx, wby + dy] +=  gvals[dx+1,dy+1] / gsum #gval / gsum

# 9X9?
kernel2d = apc.Gaussian2DKernel(SX, x_size=7, y_size=7)
for g in range(max(groups)):
    occmaps[g] = apc.convolve(occmaps[g], kernel2d)

for g in range(max(groups) + 1):
    OCCPATH = OUTBASE + 'occ_%d.mat' % g
    # transpose for consistency
    np.savetxt(OCCPATH,  occmaps[g].transpose())
print('Done occupancy map')

PLOTOCC = False
for g in range(max(groups)+1):
    if PLOTOCC:
        plt.imshow(occmaps[g].transpose())
        plt.colorbar()
        plt.show()

pfs = []
for g in range(max(groups)+1):
    pfs_g = []
    for c in range(nclu):
        pfs_g.append(np.zeros((nbinx, nbiny)))
    pfs.append(pfs_g)

DOWNSAMPLE = False

if DOWNSAMPLE:
    # if downsampling - calculate per bin
    # [SES][CELL][BIN] - array of numbers of spikes
    brates = [[[[] for b in range(nbinx * nbiny)] for c in range(ncell)] for s in range(max(groups)+1)]
    t = 0
    ires = 0
    ises = 0
    for whli in range(len(whl)):
        if speed[whli] < ST:
            continue

        bx = ri(whl[whli,0] / BIN)
        by = ri(whl[whli,1] / BIN)

        if ises < len(sessions) and whli*WHLSR > sessions[ises]:
            ises += 1

        pop = [0] * ncell
        t = whli * WHLSR
        while ires < len(res) and res[ires] < t + WHLSR:
            pop[clu[ires]] += 1
            ires += 1

        for c in range(ncell):
            # TODO: don't write 0s if too much memory used ... random sample twice: 0/non-0 => value if non-0
            try:
                brates[groups[ises]][c][nbinx * by + bx].append(pop[c])
            except:
                print('bx,by,ises,c,nbinx,nbiny',bx,by,ises,c,nbinx,nbiny)
                exit(1)

    # randomly sample N samples from every rate => mult by 5 to get spikes/s => smooth ! (use more smoothing?) => check manually with gnuplot
    NSAMPLE = 3;
    for g in range(max(groups)+1):
        for c in range(ncell):
            for binx in range(nbinx):
                for biny in range(nbiny):
                    try:
                        if len(brates[g][0][nbinx * biny + binx]) > 0:
                            pfs[g][c][binx, biny] += np.sum(choices(brates[g][c][nbinx * biny + binx], NSAMPLE))
                    except:
                        print(g, len(brates), 'g')
                        print('zero', len(brates[g]))
                        print(nbinx * biny + binx, len(brates[g][0]), 'bins')

    # SET NONE?
    for g in range(max(groups)+1):
        for binx in range(nbinx):
            for biny in range(nbiny):
                if len(brates[g][0][nbinx * biny + binx]) == 0:
                    for c in range(ncell):
                        pfs[g][c][binx, biny] = np.nan

else:
    whlscale = WHLSR
    ises = 0
    for i in range(len(clu)):
        whlt = min(int(np.round(res[i]/WHLSR)), len(whl)-1)
        x = whl[whlt, 0]
        y = whl[whlt, 1]
        wbx = ri(x / BIN)
        wby = ri(y / BIN)

        if speed[whlt] < ST or not istrainwhlt(whlt):
            continue

        if ises < len(sessions) and res[i] > sessions[ises]:
            ises += 1

        gsum = 0
        gvals = np.zeros((3,3))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if wbx + dx < 0 or wbx + dx >= nbinx or wby + dy < 0 or wby + dy >= nbiny:
                    continue
                gval =  np.exp((-(wbx + dx + 0.5 - x/BIN)**2 - (wby + dy + 0.5 - y/BIN)**2))
                # occmap[wbx + dx, wby + dy] == gval
                gvals[dx+1,dy+1] = gval
                gsum += gval

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if wbx + dx < 0 or wbx + dx >= nbinx or wby + dy < 0 or wby + dy >= nbiny:
                    continue

                #gval =  np.exp(-((wbx + dx + 0.5 - x/BIN)**2 - (wby + dy + 0.5 - y/BIN)**2)/SX)
                try:
                    pfs[groups[ises]][clu[i]][wbx + dx, wby + dy] += gvals[dx+1,dy+1] / gsum #gval / gsum
                except:
                    print(wbx,wby,dx,dy,nbinx,nbiny)
                    exit(0)

# divide by occupancy
#gkern = kernel(9, SX)

#POSSR = 39.0625
POSSR = 50.0

warned_fe = False
for g in range(max(groups)+1):
    for c in range(nclu):
        # 50 hz = position sampling rate (every WHLSR data samples)

        pfs[g][c][np.isinf(pfs[g][c])] = np.nan
        nanmap = np.isnan(pfs[g][c])
        pfs[g][c] = apc.convolve(pfs[g][c], kernel2d)

        if DOWNSAMPLE:
            pfs[g][c] *= 50 / NSAMPLE
        else:
            pfs[g][c] /= occmaps[g] / POSSR

        pfs[g][c][occmaps[g] < OT] = np.nan
 
        #pfs[c] = nd.filters.convolve(pfs[c], gkern, mode = 'constant')
        pfs[g][c][nanmap] = np.nan
        pfs[g][c] = apc.convolve(pfs[g][c], kernel2d)

        pfs[g][c][nanmap] = np.nan
        pfs[g][c][occmaps[g] < OT] = np.nan

        PFPATH = '%s%d_%d.mat' % (OUTBASE, c, g)
        if os.path.isfile(PFPATH) and not warned_fe:
            print('WARNING File exists at PF output path, delete first!')
            warned_fe = True
            # exit(1)
        # transpose for consistenc
    # transpose for consistencty
        np.savetxt(PFPATH, pfs[g][c].transpose())

        if PLT:
            plt.figure(figsize=(20,12))
            plt.imshow(pfs[g][c].transpose())
            plt.colorbar()
            plt.show()
