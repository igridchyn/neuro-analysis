#!/usr/bin/env python

from matplotlib import pyplot as  plt
import numpy as np
from numpy import log, genfromtxt, sqrt
from sys import argv
import os.path
from tracking_processing import whl_to_pos, whl_to_speed
#======================================================================================================================================================
if len(argv) < 9:
	print 'Usage: ' + argv[0] + '(1)<prediction likelihood matrix path prefix> (2)<whl file> (3)<start time> (4)<time step (window)> (5)<bin size> (6)<environments x border (not BIN)> (7)<speed threshold> (8)<normalize likelihoods : 0/1>'
	print 'Analyze the learning session decoding dump of the LFPO (likelihood matrices for each window)'
	exit(0)
#======================================================================================================================================================
def read_from_mats():
	global time1, whl
	for pred in preds:
		if len(pred.shape) > 1:
			mx1 = np.max(pred[:,0:nbx/2])
			mx2 = np.max(pred[:,nbx/2:])
			norm = log(np.sum(np.exp(pred)))
		else:
			mx1 = np.max(pred[0:nbx/2])
			mx2 = np.max(pred[nbx/2:])
			norm = log(np.sum(np.exp(pred - 100))) + 100
			# print norm
		confidence = mx1 - mx2
		if confidence < 0:
			confidence = -confidence
		# confidence -= norm
		gtx = whl[time1/480][0]
		gty = whl[time1/480][1]
		argm = np.argmax(pred)
		px = (argm % nbx + 0.5) * sbin
		py = (argm / nbx + 0.5) * sbin
		spd = speed[time1/480]
		if spd < speed_thold or normlik and np.isinf(confidence):
			classifications.append(-1)
		else:
			classifications.append((px-envborder)*(gtx-envborder)>0)
			confidences.append(confidence)
			errors.append(sqrt((px-gtx)**2 + (py-gty)**2))
			mlikes1.append(mx1 - norm if normlik else 0)
			mlikes2.append(mx2- norm if normlik else 0)
		time1 += step

#======================================================================================================================================================

predpathpref = argv[1]
whlpath = argv[2]
start = int(argv[3])
step = int(argv[4])
sbin = float(argv[5])
envborder = float(argv[6])
speed_thold = float(argv[7])
normlik = bool(int(argv[8]))

# predictions
preds = []
time1 = start + step

while os.path.isfile('%s%d.mat'%(predpathpref, time1)):
	pred = genfromtxt('%s%d.mat'%(predpathpref, time1))
	preds.append(pred.transpose())
	time1 += step

print 'Loaded %d decoded positions starting with %d and ending with %d' % (len(preds), start, time1-step)

if len(preds[0].shape) > 1:
	nbx = preds[0].shape[1]
	nby = preds[0].shape[0]
else:
	nbx = preds[0].shape[0]
	nby = 1

print 'Size of the environment : %d X %d bins = %.2f X %.2f' % (nbx, nby, nbx*sbin, nby*sbin)

# calc whl, speed
whl = whl_to_pos(open(argv[2]), False)
speed = whl_to_speed(whl)

# dump confidences, errors, classifications
classifications = []
errors = []
confidences = []
mlikes1 = []
mlikes2 = []

time1 = start + step
read_from_mats()

outdir = 'wsbased_out_' + str(start) + '_' + str(time1) +'/'
if not os.path.isdir(outdir):
        os.mkdir(outdir)

# dump comfidences, calssifications and errors
fconf = open(outdir + 'confidences.txt', 'w')
for conf in confidences:
        fconf.write('%f\n' % conf)
fclsf = open(outdir + 'clsf.txt', 'w')
for cl in classifications:
        fclsf.write('%d\n' % cl)
ferrors = open(outdir + 'errors.txt', 'w')
for error in errors:
        ferrors.write('%d\n' % error)
fmlikes1 = open(outdir + 'mlikes1.txt', 'w')
for mlike in mlikes1:
	fmlikes1.write('%f\n' % mlike)
fmlikes2 = open(outdir + 'mlikes2.txt', 'w')
for mlike in mlikes2:
	fmlikes2.write('%f\n' % mlike)
