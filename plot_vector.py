#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

if len(argv) < 2:
	print 'USAGE: (1)<vector file>'
	exit(0)

vec = np.loadtxt(argv[1])
vec /= np.sum(vec)

#plt.figure(figsize = (6,3))
f, (ax1, ax2) = plt.subplots(1, 2, figsize = (10,8), sharey=True)

#plt.plot(vec, linewidth=5)
ax1.plot(vec[:85], linewidth=5)
ax2.plot(vec[90:], linewidth=5, color = 'red')

lfs = 30
#plt.xlabel('Spatial bin', fontsize=lfs)
ax1.set_xlabel('Spatial bin', fontsize=lfs)
ax2.set_xlabel('Spatial bin', fontsize=lfs)
ax1.set_title('Control environment', fontsize=lfs)
ax2.set_title('Target environment', fontsize=lfs)

ymax = 0.025
ax1.set_ylim([0, ymax])
ax2.set_ylim([0, ymax])

ax1.text(-15, ymax*1.1, 'A', fontsize=lfs+20, fontweight = 'bold')
ax2.text(-15, ymax*1.1, 'B', fontsize=lfs+20, fontweight = 'bold')

plt.sca(ax1)
set_xticks_font(20)
set_yticks_font(20)
plt.sca(ax2)
set_xticks_font(20)

#plt.ylabel('Probability', fontsize=lfs)
ax1.set_ylabel('Probability', fontsize=lfs)

am = np.argmax(vec) - 90
ax2.plot([am, am], [0, vec[am + 90]], linewidth = 3, color = 'black')

fs = 30
#plt.text(15, 0.001, 'CONTROL', fontsize=fs)
#plt.text(115, 0.001, 'TARGET', fontsize=fs)

am = np.argmax(vec)
#plt.plot([am, am], [0, vec[am]], color = 'black', linewidth=3)
print vec[am]
am1 = np.argmax(vec[:len(vec) / 2])
print vec[am1]

plt.subplots_adjust(bottom=0.15, top=0.85)

plt.show()
