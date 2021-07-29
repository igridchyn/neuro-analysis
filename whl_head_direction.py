#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt
from tracking_processing import whl_to_pos, whl_to_speed
from sys import argv
from math import atan2, cos, sin, sqrt

def whl_angle_at(i):
        bx = whl[i][0] / BIN
        by = whl[i][1] / BIN

        bx2 = whl[i-1][0] / BIN
        by2 = whl[i-1][1] / BIN

        if bx > LIM or by > LIM or bx2 > LIM or by2 > LIM:
                return 0, False

        angle = atan2(bx-bx2, by-by2)
	
	return angle, True

#=======================================================================================================================

if len(argv) < 2:
	print 'Usage: (1)<whl file>'
	print 'Calculate head direction at every whl point'
	exit(0)

whl = whl_to_pos(open(argv[1]), False)

BIN = 4
NBX = 80
NBY = 45

hd = np.zeros((NBX, NBY))
hdo = np.zeros((NBX, NBY))
hdinst = np.zeros((NBX, NBY))
hdinsto = np.zeros((NBX, NBY))
cosi = np.zeros((NBX, NBY))
sini = np.zeros((NBX, NBY))

LIM = 400
RAD = 16
OKTHOLD = 10

for i in range(RAD, len(whl) - RAD):
	bx = whl[i][0] / BIN
	by = whl[i][1] / BIN

	bx2 = whl[i-1][0] / BIN
	by2 = whl[i-1][1] / BIN

	if bx > LIM or by > LIM or bx2 > LIM or by2 > LIM:
		continue

	angle = atan2(bx-bx2, by-by2)

	cosi[bx, by] += cos(angle)	
	sini[bx, by] += sin(angle)	
	hdo[bx, by] += 1

	# calculate instant HD as instant circular variance
	sinsum = 0
	cossum = 0
	nok = 0
	for j in range(-RAD + 1, RAD + 1):
		an, aok = whl_angle_at(i + j)
		if (aok):
			nok += 1
			sinsum += sin(an)
			cossum += cos(an)
	
	if nok > OKTHOLD:
		hdinst[bx, by] += 1 - sqrt(cossum ** 2 + sinsum ** 2) / nok
		hdinsto[bx, by] += 1

	# !!! TODO: speed vs HD - COLORMAP !!!

for x in range(NBX):
	for y in range(NBY):
		hd[x, y] = 1 - sqrt(cosi[x,y] ** 2 + sini[x,y] ** 2) / hdo[x,y]

plt.figure()
#plt.imshow(hdo, interpolation = 'none')
plt.imshow(hdinst / hdinsto, interpolation = 'none')
plt.show()
