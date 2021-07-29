#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats
from tracking_processing_p3 import *

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def in_sec(sec, pos):
	for i in range(sec.shape[0] - 1):
		ex = sec[i+1,0] - sec[i,0]
		ey = sec[i+1,1] - sec[i,1]

		wx = pos[0] - sec[i,0]
		wy = pos[1] - sec[i,1]
	
		if ex*wy - ey*wx < 0:
			return True
		
	return False

if len(argv) < 4:
	print('USAGE: (1)<whl> (2)<sector edges> (3)<output prefix - APPENDED>')
	exit(0)

WHL_LONG = False
whl = np.loadtxt(argv[1])
if len(whl[0,:]) > 2:
	whl = whl_to_pos(open(argv[1]), True)
	WHL_LONG = True
else:
	for i in range(1, len(whl)):
		if whl[i,0] < 0:
			whl[i] = whl[i-1]

whl = np.array(whl)
speed = whl_to_speed(whl)

sec = np.loadtxt(argv[2])
if sec[0,2] < 100:
	sec *= sec[0,2]
else:
	sec *= 4.1

speeds_in = []
speeds_out = []

occ_in = 0
occ_out = 0

inds = []

STOCC = 2
for i in range(len(whl)):
	if whl[i,0] > 1000 or whl[i,0] < 0:
		inds.append(False)
		continue

	if in_sec(sec, whl[i,:]):
		speeds_in.append(speed[i])
		if speed[i] > STOCC:
			occ_in += 1
	else:
		speeds_out.append(speed[i])
		if speed[i] > STOCC:
			occ_out += 1

	inds.append(in_sec(sec, whl[i,:]))

inds = np.array(inds)
#plt.plot(whl[inds,0], whl[inds,1])
#plt.plot(sec[:,0], sec[:,1])
#plt.show()

#plt.hist(speeds_in, bins=50, alpha=0.5)
#plt.hist(speeds_out, bins=50, color='red', alpha=0.5)


# NORMALIZE OCCS BY SIZE OF THE SECTOR!
if sec.shape[0] > 2:
	# then its 3 points - 2 vectors, use angle between them!
	scale_in = (np.pi - angle_between(sec[2,:]-sec[1,:], sec[1,:]-sec[0,:])) / np.pi
	scale_out = 2 - scale_in
else:
	scale_in = 1
	scale_out = 1
	
print('In/out scale: %.2f / %.2f' % (scale_in, scale_out))
occ_in /= scale_in
occ_out /= scale_out

speeds_in = np.array(speeds_in)
speeds_out = np.array(speeds_out)
ST = -1
# speed is in 16 samples
SFAC = 50/16 if WHL_LONG else 39/16 
print('Speeds: %.2f / %.2f' % (np.mean(speeds_in[speeds_in > ST]) * SFAC, np.mean(speeds_out[speeds_out > ST]) * SFAC))
print('Occupancies: %d / %d' % (occ_in, occ_out))

fouts = [open(argv[3]+str(i), 'a') for i in range(4)]
vals =[np.mean(speeds_in[speeds_in > ST]) * SFAC, np.mean(speeds_out[speeds_out > ST]) * SFAC, occ_in, occ_out]
#fout.write('%.2f %.2f %d %d\n' % (np.mean(speeds_in[speeds_in > ST]), np.mean(speeds_out[speeds_out > ST]), occ_in, occ_out))
for i in range(4):
	fouts[i].write('%.2f\n' % vals[i])
