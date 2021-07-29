#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
from scipy import stats
from tracking_processing_p3 import *

if len(argv) < 3:
    print('USAGE: (1)<whl> (2)<intervals (24 kHz)> [OPT](3)<sector file>')
    print('Plot whl in intervals, optionally - sector')
    exit(0)

#whl = whl_to_pos(open(argv[1]), True)
whl = np.loadtxt(argv[1])

ints = np.loadtxt(argv[2], dtype=int)

HAVESEC = len(argv) > 3

if HAVESEC:
    sec = np.loadtxt(argv[3])

WHL_SR = 480
#WHL_SR = 512

whli = 0
whl_ints = []
whl_out = []

for ii in range(len(ints)):
	while whli < ints[ii][0] // WHL_SR:
		whl_out.append(whl[whli])
		whli += 1
	#whli = ints[ii][0] // WHL_SR
	while whli < ints[ii][1] // WHL_SR:
		whl_ints.append(whl[whli])
		whli += 1

whl_ints = np.array(whl_ints)
whl_out = np.array(whl_out)

plt.scatter(whl_ints[:,0], whl_ints[:,1], s=0.5)
#plt.scatter(whl_out[:,0], whl_out[:,1], color='red', s=0.5)

SCALE = 4
#sec[0] /= SCALE
#sec[1] /= SCALE
#x1 = sec[0]
#y1 = sec[1]
#ang1 = np.pi/2 - sec[2]/180*np.pi
#x2 = sec[0] + 50*np.cos(ang1)
#y2 = sec[1] + 50*np.sin(ang1)
#ang2 = ang1 - sec[3]/180*np.pi
#x3 = sec[0] + 50*np.cos(ang2)
#y3 = sec[1] + 50*np.sin(ang2)

#plt.plot([sec[0], sec[2]], [sec[1], sec[3]])
#plt.plot([x2,x1,x3], [y2,y1,y3], color='black')

if HAVESEC:
    sec *= 4.1 if sec[0,-1] > 99 else sec[0,-1] # 4.1 default or last col
    plt.plot(sec[:,0], sec[:,1])
    plt.scatter(sec[-1,0], sec[-1,1], s=20, color='black')

plt.show()
