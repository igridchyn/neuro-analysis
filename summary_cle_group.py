#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *
from scipy.stats import ttest_ind_from_stats, mannwhitneyu
from matplotlib import gridspec

if len(argv) < 5:
	print 'USAGE: (1)<inh sum> (2)<inh top20 sum> (3)<ninh sum> (4)<INH/DINH>'
	exit(0)

fsuml = open(argv[1])# + '.combcorrs')
fsumtopl = open(argv[2])# + '.combcorrs')
fsumnol = open(argv[3])# + '.combcorrs')

resptype = argv[4]
if resptype not in ['DINH', 'INH']:
	print '4-th parametere is INH or DINH'
	exit(0)
DINH = resptype == 'DINH'

# IDX = 0 for inh, 10 for DINH
IDX = 0 if DINH else 10
print 'WARNING: IDX = ', IDX
for i in range(4*IDX):
        fsuml.readline()
        fsumtopl.readline()
        fsumnol.readline()

# line rates light before
lrlb = fsuml.readline()
# line rates light after
lrla = fsuml.readline()

# line rates no light before
lrnlb = fsumnol.readline()
# line rates no light after
lrnla = fsumnol.readline()

# line rates TOP-20% light before
lrtlb = fsumtopl.readline()
# line rates TOP-20% light after
lrtla = fsumtopl.readline()

# ORDER: light, top 20% light, no light; before -> after
# 	[0] : control; [1] : target
print [lrnlb, lrnla, lrtlb, lrtla, lrlb, lrla]
#infos = [[float(f) for f in line.split(' ')] for line in [lrlb, lrla, lrtlb, lrtla, lrnlb, lrnla]]

#infos = [[float(f) for f in line.split(' ')] for line in [lrnlb, lrnla, lrtlb, lrtla, lrlb, lrla]]
#rates = [info[:2]  for info in infos]
#stds =  [info[2:4] for info in infos]
#ns =    [info[4:] for info in infos]



# IN CASE OF RATES WRITTEN TO FILE
rawrates= [[float(f) for f in line.split(' ') if f != '\n'] for line in [lrnlb, lrnla, lrtlb, lrtla, lrlb, lrla]]
# split lines into c/t
raw_rates = []
ns = []
for rawrate in rawrates:
	n1 = int(rawrate[0])
	raw_rates.append([rawrate[1:n1+1], rawrate[n1+2:]])
	ns.append([n1, len(rawrate)-n1-2])
rates = [[np.mean(rr[0]), np.mean(rr[1])] for rr in raw_rates]
stds = [[np.std(rr[0]), np.std(rr[1])] for rr in raw_rates]
ns = [[len(rr[0]), len(rr[1])] for rr in raw_rates]


sems = [stds[i] / np.sqrt(ns[i]) for i in range(6)]
ps = [ttest_ind_from_stats(rates[i][0], stds[i][0], ns[i][0], rates[i][1], stds[i][1], ns[i][1], equal_var = False) for i in range(6)]
#ps = [mannwhitneyu(rr[0], rr[1]) for rr in raw_rates]
sigs =  [p_to_sig_str(p[1]) for p in ps]
stats =  [p[0] for p in ps]

print 'P-VALUES', [p[1] for p in ps]
print 'STATS   ', stats
print 'NS', ns

if DINH:
	# fig2, (ax1, ax2) = plt.subplots(2,1, figsize=(12,8)) #, gridspec_kw = {'height_ratios':[3, 1]})
	fig2 = plt.figure(figsize=(12,6)) #, gridspec_kw = {'height_ratios':[3, 1]})
	gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3]) 
	ax1 = plt.subplot(gs[0])
	ax2 = plt.subplot(gs[1])

	xb_c_2 = np.array((10,17))
	xb_t_2 = xb_c_2 + 1

	ax1.bar(xb_c_2, [rates[i][0] for i in [3,5]])
	ax1.bar(xb_t_2, [rates[i][1] for i in [3,5]], color = 'r')

	# REV1 0-2.5 + 8.2-11
	ax1.set_ylim([8.2, 11])
	ax2.set_ylim([0, 3.5])

	ax1.set_yticks([10])

	ax2.set_yticks([0, 1, 2, 3])
else:
	fig2, ax2 = plt.subplots(1,1, figsize=(12,6))

xb_c = np.array((0,3,7,10,14,17))
xb_t = xb_c + 1
ax2.bar(xb_c, [rates[i][0] for i in range(6)])
ax2.bar(xb_t, [rates[i][1] for i in range(6)], color = 'r')

bw = 0.8
for i in range(6):
	ax2.text(xb_c[i] + bw/2, max(rates[i])+max(sems[i])*2, sigs[i], fontsize=20)

# label groups of events
lims = [max(rates[i][0]+sems[i][0], rates[i][1]+sems[i][1]) for i in range(6)]
LABHEIGHT = max(lims) + 1

GLFS = 25
ax2.text(15,  LABHEIGHT, 'Disrutped', fontsize=GLFS)
ax2.text(6.5,  LABHEIGHT, 'Top 20% disrupted', fontsize=GLFS)
ax2.text(1, LABHEIGHT, 'Control', fontsize=GLFS)

clabs = ['Control', 'Target']
# 0=top right, 3=bottom left, 4 = bottom right, 6=middle left, 5=middle right ?, 
ax2.legend(clabs, loc=5, fontsize=GLFS)

for i in range(6):
	ax2.errorbar(xb_c[i] + bw/2, rates[i][0], yerr = sems[i][0], fmt = '.', color='black')
	ax2.errorbar(xb_t[i] + bw/2, rates[i][1], yerr = sems[i][1], fmt = '.', color='black')

if DINH:
	ii = 0
	ax2.tick_params(labeltop='off', top=False)
	ax1.tick_params(labelbottom='off', bottom=False)
	for i in [3,5]:
		ax1.errorbar(xb_c_2[ii] + bw/2, rates[i][0], yerr = sems[i][0], fmt = '.', color='black')
		ax1.errorbar(xb_t_2[ii] + bw/2, rates[i][1], yerr = sems[i][1], fmt = '.', color='black')
		ax1.text(xb_c_2[ii] + bw/2, max(rates[i])+max(sems[i])+0.1, sigs[i], fontsize=20)
		ii += 1

	plt.subplots_adjust(hspace=0.05)

#ax2.errorbar((1+bw/2,5+bw/2), (rates_nolight_before[0], rates_nolight_after[0]), yerr =  (sem_nolight_before[0], sem_nolight_after[0]), fmt = '.', color='black')
#ax2.errorbar((2+bw/2,6+bw/2), (rates_nolight_before[1], rates_nolight_after[1]), yerr =  (sem_nolight_before[1], sem_nolight_after[1]), fmt = '.', color='black')

LFS = 30
plt.ylabel('Z-scored firing rate', fontsize=LFS)
plt.xticks(xb_c + 1, ['Before\ndetection', 'After\ndetection'] * 3, fontsize = LFS-7)
set_yticks_font(LFS)
#plt.gca().get_xaxis().set_visible(False)
plt.gca().get_xaxis().set_ticks_position('bottom')
plt.gca().get_yaxis().set_ticks_position('left')

if DINH:
	ax1.set_xlim([-0.5, 19.5])
	ax2.set_xlim([-0.5, 19.5])

	plt.sca(ax1)
	set_yticks_font(LFS)
else:
	plt.xlim([-0.5, 19.5])
	plt.ylim([-0.7, LABHEIGHT+0.5])

# 0.07 for inh
plt.subplots_adjust(left=0.11, right=0.99, top=0.98, bottom=0.165)

plt.show()


# REVIEW ANALYSIS - COMAPRE RATE SCORES OF INHBIITED AND DISINHIBTED CELLS ...
# before-to-after rates scores in Control events for inbhiited vs. disinhibited cells -> separatelt for control env cells, target env cells, and all toghether


