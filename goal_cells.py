#!/usr/bin/env python
import numpy as np
from sys import argv
import os
from math import sqrt

def distance(p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

if len(argv) <  4:
	print 'USAGE: (1)<base: pf_> (2)<session 1> (3)<session 2> (4)<output>'
	exit(0)

base = argv[1]
s1 = argv[2]
s2 = argv[3]
outpath = argv[4]

binsize = 6
g1 = [0, 0]
g2 = [0, 0]

fab = open('about.txt' if os.path.isfile('about.txt') else ('../about.txt' if os.path.isfile('../about.txt') else '../../about.txt'))
for line in fab:
	if len(line) < 1:
		continue

	ws = line.split(' ')
	if ws[0] == 'g1x':
		g1[0] = float(ws[1])
	if ws[0] == 'g1y':
		g1[1] = float(ws[1])
	if ws[0] == 'g2x':
		g2[0] = float(ws[1])
	if ws[0] == 'g2y':
		g2[1] = float(ws[1])

print 'Goals: ', g1, g2

c = 1
pfpath1 = base + str(c) +  '_' + s1 + '.mat'

print pfpath1

while os.path.isfile(pfpath1):
	pf1 = np.genfromtxt(pfpath1)
	imaxx1 = np.nanargmax(pf1) % pf1.shape[1]
	imaxy1 = np.nanargmax(pf1) / pf1.shape[1]

	pfpath2 = base + str(c) + '_' + s2 + '.mat'
	pf2 = np.genfromtxt(pfpath2)
	imaxx2 = np.nanargmax(pf2) % pf2.shape[1]
	imaxy2 = np.nanargmax(pf2) / pf2.shape[1]

	imaxx1 = (imaxx1 +0.5) * binsize
	imaxy1 = (imaxy1 +0.5) * binsize
	imaxx2 = (imaxx2 +0.5) * binsize
	imaxy2 = (imaxy2 +0.5) * binsize

	rad = 30
	if distance(g1, [imaxx1, imaxy1]) < rad or distance(g1, [imaxx2, imaxy2])< rad:
		print 'Goal 1 cell: ', c
	if distance(g2, [imaxx2, imaxy2]) < rad or distance(g2, [imaxx1, imaxy1]) < rad:
		print 'Goal 2 cell: ', c
	
	c += 1
	pfpath1 = base + str(c) + '_' + s1 + '.mat'
