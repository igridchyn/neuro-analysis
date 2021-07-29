#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats

if len(argv) < 2:
	print('USAGE: (1)<base of inoutstat files (before session number) files>')
	exit(0)

# 4 FIGURES: SPEED/OCCUPANCY RAW COMPARISON AND RATIO

SPEED_SCALE = 1
TIME_SCALE = 50
BASE = argv[1]

speed =  [(np.loadtxt(BASE+'%d_0' % s) * SPEED_SCALE, np.loadtxt(BASE+'%d_1' % s) * SPEED_SCALE)  for s in [2, 6, 8] ]
occ =  [(np.loadtxt(BASE+'%d_2' % s) / TIME_SCALE, np.loadtxt(BASE+'%d_3' % s) / TIME_SCALE) for s in [2, 6, 8] ]

(f, ax) = plt.subplots(2, 2, figsize=(10, 10))
sn = np.sqrt(len(occ[0][0]))

# occ bars
for s in range(3):
	bx = [s*3, s*3+1]
	ax[0,0].bar(bx, [np.mean(speed[s][0]), np.mean(speed[s][1])], color=['black', 'green'])
	ax[0,0].errorbar(bx, [np.mean(speed[s][0]), np.mean(speed[s][1])], yerr=[np.std(speed[s][0])/sn, np.std(speed[s][1])/sn], fmt='.', color='black')

# occupancy bars
for s in range(3):
	bx = [s*3, s*3+1]
	ax[0,1].bar(bx, [np.mean(occ[s][0]), np.mean(occ[s][1])], color=['black', 'green'])
	ax[0,1].errorbar(bx, [np.mean(occ[s][0]), np.mean(occ[s][1])], yerr=[np.std(occ[s][0])/sn, np.std(occ[s][1])/sn], fmt='.', color='black')

#LOGRAT = False
LOGRAT = True

# speed ratio
for s in range(3):
	bx = [s*2]
	if not LOGRAT:
		rats = np.divide(speed[s][0], speed[s][1])
	else:
		rats = np.log(np.divide(speed[s][0], speed[s][1]))
	print(stats.ttest_1samp(rats, 0 if LOGRAT else 1))
	ax[1,0].bar(bx, [np.mean(rats)], color=['black'])
	ax[1,0].errorbar(bx, [np.mean(rats)], yerr=[np.std(rats)/sn], fmt='.', color='black')

# occ ratio
for s in range(3):
	bx = [s*2]
	if not LOGRAT:
		rats = np.divide(occ[s][0], occ[s][1])
	else:
		rats = np.log(np.divide(occ[s][0], occ[s][1]))
	print(stats.ttest_1samp(rats, 0 if LOGRAT else 1))
	ax[1,1].bar(bx, [np.mean(rats)], color=['black'])
	ax[1,1].errorbar(bx, [np.mean(rats)], yerr=[np.std(rats)/sn], fmt='.', color='black')

YLFS = 20
ax[0,0].set_ylabel('Mean speed [cm/s]', fontsize=YLFS)
ax[0,1].set_ylabel('Time spend [s]', fontsize=YLFS)
#ax[1,0].set_ylabel('Speed ratio', fontsize=YLFS)
#ax[1,1].set_ylabel('Occupancy ratio', fontsize=YLFS)
ax[1,0].set_ylabel('Speed ratio' + (', log' if LOGRAT else ''), fontsize=YLFS)
ax[1,1].set_ylabel('Occupancy ratio' + (', log' if LOGRAT else ''), fontsize=YLFS)

SLABS = ['FAM1', 'FAML', 'FAM2']
TFS = 15
for yx in range(2):
	ax[0, yx].set_xticks([0.5, 3.5, 6.5])
	ax[0, yx].set_xticklabels(SLABS, fontsize = TFS)
	ax[1, yx].set_xticks([0, 2, 4])
	ax[1, yx].set_xticklabels(SLABS, fontsize = TFS)

	ax[0, yx].spines['right'].set_visible(False)
	ax[0, yx].spines['top'].set_visible(False)
	ax[1, yx].spines['right'].set_visible(False)
	ax[1, yx].spines['top'].set_visible(False)

plt.tight_layout()
plt.show()
