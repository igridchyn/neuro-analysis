#!/usr/bin/env python

from matplotlib import pyplot as plt
import statsmodels as sm
import statsmodels.distributions
from sys import argv

def find_levels(l):
	liw = 0
	while liw < len(ecdfw.y) and ecdfw.y[liw] < l:
		liw += 1
	xl = ecdfw.x[liw]

	lis = 0
	while lis < len(ecdfs.x) and ecdfs.x[lis] < xl:
		lis += 1

	return liw, lis
	
# load first / second confidences

#pathw = '/home/igor/code/ews/lfp_online/sdl_example/Debug/confs.txt'
#print 'WARNING: waking confidences taken from ...', pathw

if len(argv) < 3:
	print 'Usage: (1)<path to file with confidences  (sleep) > (2)<path to file with confidences 2 (waking/shuffled)> (3)<swap>'
	print 'Plot ECDF of numbers in two files ...'

pathw = argv[2]

confss = [float(c) for c in open(argv[1]) if len(c) > 0]
confsw = [float(c) for c in open(pathw) if len(c) > 0 and 'lax' not in c]

swap = bool(int(argv[3]))
if swap:
	confss = [-c for c in confss]

ecdfs = statsmodels.distributions.ECDF(confss)
ecdfw = statsmodels.distributions.ECDF(confsw)

lw = 3

plt.plot(ecdfw.x, ecdfw.y, linewidth=lw)
plt.plot(ecdfs.x, ecdfs.y, color = 'r', linewidth=lw)

# plot line from 40/60 levels of waking
liw1, lis1 = find_levels(0.4)
liw2, lis2 = find_levels(0.6)

print liw2, lis2

plt.plot([ecdfw.x[liw1], ecdfw.x[liw1]], [ecdfw.y[liw1], ecdfs.y[lis1]], linewidth=lw)

print 'WARNING: disabled level plotting'
#if lis2 == len(ecdfs.x):
#	plt.plot([ecdfw.x[liw2], ecdfw.x[liw2]], [ecdfw.y[liw2], 1.0], color = 'g', linewidth=lw)	
#else:
#	plt.plot([ecdfw.x[liw2], ecdfw.x[liw2]], [ecdfw.y[liw2], ecdfs.y[lis2]], color='g', linewidth=lw)

plt.grid()
plt.legend(['Shuffled sleep', 'Sleep'], loc=0)
plt.show()
