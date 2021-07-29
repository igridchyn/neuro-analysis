#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

def RGB(red,green,blue): return '#%02x%02x%02x' % (red,green,blue)

if len(argv) < 2:
	print 'USAGE: (1)<list of directories>'
	exit(0)

# full matrices of firing rates b/a
mresp = []
# responses
resp = []

for line in open(argv[1]):
	if len(line) < 2:
		continue
	
	#mresp.append(np.loadtxt(line[:-1] + '/full.responses'))
	#mresp.append(np.loadtxt(line[:-1] + '/full.05ms.responses'))
	mresp.append(np.loadtxt(line[:-1] + '/full.05ms.w50.responses'))
	resp.append(read_float_list(line[:-1] + '/pulses.timestamps.responses'))

# calculate mean response for inhibited / disinhibited cells
#meanr_inh = np.zeros((mresp[0].shape[1], 1))
meanr_inh = np.zeros((1, mresp[0].shape[1]))
meanr_dinh = np.zeros((1, mresp[0].shape[1]))
meanr_int = np.zeros((1, mresp[0].shape[1]))

print 'Shape of responses:', meanr_inh.shape

#print meanr_inh.shape
ITHOLD = -0.2877
DITHOLD = 0.693
INTTHOLD = 20

ni = 0
ndi = 0
nint = 0

r_inh = []
r_dinh = []
r_int = []

norms = []

# to plot absolute rates instead of normalized
ABSRATE = False

for d in range(len(mresp)):
	for c in range(len(resp[d])):
		#if (ITHOLD < 0 and resp[d][c] > ITHOLD) or (ITHOLD > 0 and resp[d][c] < ITHOLD):
		if resp[d][c] > ITHOLD and resp[d][c] < DITHOLD:
			continue

		# normalize by before-rate
		norm = np.sum(mresp[d][c, 11:21]) / 10.0
		norms.append(norm)

		#print norm
		#print mresp[d].shape
		#print mresp[d][c,:]
                
		if norm > INTTHOLD:
                        if ABSRATE:
                            norm = 1
			meanr_int += (mresp[d][c,:] / norm)
			r_int.append(mresp[d][c, :] / norm)
			nint += 1
		elif norm > 0:
                        if ABSRATE:
                            norm = 1
			if resp[d][c] < 0:
				meanr_inh += (mresp[d][c, :] / norm)
				r_inh.append(mresp[d][c, :] / norm)
				ni += 1
			else:
				meanr_dinh += (mresp[d][c, :] / norm)
				r_dinh.append(mresp[d][c, :] / norm)
				ndi += 1

print 'Number of cells inh / dinh / int :', ni, ndi, nint
print 'Normalizers:', np.mean(norms), norms

meanr_inh /= ni
meanr_dinh /= ndi
meanr_int /= nint

r_inh = np.array(r_inh)
r_dinh = np.array(r_dinh)
r_int = np.array(r_int)

#if ABSRATE:
#    meanr_inh = np.log(meanr_inh)
#    meanr_dinh = np.log(meanr_dinh)
#    meanr_int = np.log(meanr_int)
    #r_inh = np.log(r_inh)
    #r_dinh = np.log(r_dinh)
    #r_int = np.log(r_int)

nsq = np.sqrt(r_inh.shape[0])
nsq_d = np.sqrt(r_dinh.shape[0])
nsq_int = np.sqrt(r_int.shape[0])

print 'RINH', r_inh.shape

std_inh = np.array([np.nanstd(r_inh[:, t]) / nsq for t in range(len(r_inh[0]))])
std_dinh = np.array([np.nanstd(r_dinh[:, t]) / nsq_d for t in range(len(r_dinh[0]))])
std_int = np.array([np.nanstd(r_int[:, t]) / nsq_int for t in range(len(r_int[0]))])

# print meanr_inh

li = list(np.transpose(meanr_inh))
ldi = list(np.transpose(meanr_dinh))
lint = list(np.transpose(meanr_int))

#plt.scatter(range(61), l)
#print len(l)
#plt.plot(range(61), l)

plt.figure(figsize=(9,6))

#bx = [-150 + 5*i for i in range(60)]
#bx = [-20 + 0.5*i for i in range(80)]
bx = [-40 + 0.5*i for i in range(mresp[0].shape[1]-1)]
#plt.bar(bx, l[1:], width=0.35) #3.5 for 5 ms
lw = 2
plt.plot(bx, li[1:], linewidth=lw)
plt.plot(bx, ldi[1:], color=RGB(255,165,0), linewidth=lw)
#plt.plot(bx, lint[1:], color='cyan', linewidth=lw)
plt.plot(bx, lint[1:], color='black', linewidth=lw)

print std_inh.shape
print np.array(li).shape
print len(bx)
yl = np.array(li[1:])[:,0] - std_inh[1:]
yt = np.array(li[1:])[:,0] + std_inh[1:]

print yl.shape
plt.fill_between(bx, yl, yt, alpha=0.3)

yld = np.array(ldi[1:])[:,0] - std_dinh[1:]
ytd = np.array(ldi[1:])[:,0] + std_dinh[1:]
plt.fill_between(bx, yld, ytd, color=RGB(255,50,0), alpha=0.3)

yld = np.array(lint[1:])[:,0] - std_int[1:]
ytd = np.array(lint[1:])[:,0] + std_int[1:]
#plt.fill_between(bx, yld, ytd, color='cyan', alpha=0.3)
plt.fill_between(bx, yld, ytd, color='grey', alpha=0.5)

plt.xlim([-40, 40])
#plt.xlim([-30, 30])
#plt.grid()

if ABSRATE:
    plt.gca().set_yscale('log')
strip_axes()

lfs = 45
#plt.xlabel('Time w.r.t. to light, ms', fontsize = lfs)
plt.xlabel('ms', fontsize = lfs)
plt.ylabel('Firing rate', fontsize = lfs)

set_xticks_font(38)
set_yticks_font(38)
plt.subplots_adjust(left=0.13, bottom=0.21, right=0.95, top=0.95)
#plt.xticks([-40, -20, 0, 20, 40])
# FOR FINE SCALE


#plt.title('Mean light response, inhibited cells')
#plt.title('Mean light response, disinhibited cells')
# plt.title('Mean light response')
plt.legend(['INHIBITED', 'DISINHIBITED', 'INTERNEURONS'], loc='best', fontsize = 20)

plt.axvline(x = 0, linewidth = 2, color='black', linestyle='--')

plt.xlim([-6, 6])
plt.xticks([-6, -4, -2, 0, 2, 4, 6])
if not ABSRATE:
    plt.ylim([0, 2.5])

plt.tight_layout()
strip_axes(plt.gca())
plt.show()
