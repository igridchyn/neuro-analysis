#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
import os
import glob
from call_log import *
from iutils import *
from scipy.stats import pearsonr, spearmanr
import statsmodels.distributions as smd
import scipy

def accuracies(path):
	f = open(path)
	ls = f.readline()
	f.readline()

	wls = ls.split(' ')
	if len(wls) > 1:
		BORD = int(wls[1])
	else:
		print 'WARNING: default border value used !'
		BORD = BORD_DEF

	# spike number bins; try global
	#sn_bins = range(0, 500, 5)
	#sn_tot = [0] * len(sn_bins)
	#sn_corr = [0] * len(sn_bins)

	correct = []
	confs = []
	errs = []
	sns = []
	corrs = []

	for line in f:
		ws = line.split(' ')
		if len(ws) < 6 or ws[2] == '1023':
			continue

		xp = float(ws[0])
		xr = float(ws[2])
		l1 = float(ws[4])
		l2 = float(ws[5])
		ltot = float(ws[6])
		correct.append((xp - BORD) * (xr - BORD) > 0)
		confs.append(abs(l1-l2)/ltot)
		errs.append(abs(xp-xr))
		if len(ws) > 7:
			sn = int(ws[7])
			sns.append(sn)
			snb = sn / 5
			sn_tot[snb] += 1
			sn_corr[snb] += int((xp - BORD) * (xr - BORD) > 0)
			corrs.append(int((xp - BORD) * (xr - BORD) > 0))

	aconfs = np.argsort(confs)
	correct_s = np.array(correct)[aconfs]

	accs = []
	for i in range(100):
		ni = len(confs) * i / 100
		accs.append(np.sum(correct_s[:ni]) / float(ni))

	return accs, errs, sns, corrs
#======================================================================================================================


if len(argv) < 2:
	print 'USAGE: (1)<file path - list of > (2)<env border>'
	exit(0)

ld = log_call(argv)

# default value - if not present in dec_bay.txt
BORD_DEF = float(argv[2])
LFS = 30

# spike number bins; try global
sn_bins = range(0, 500, 5)
sn_tot = [0] * len(sn_bins)
sn_corr = [0] * len(sn_bins)

# all ... - for every day
aaccs = []
aerrs = []
asns = []
acorrs = []

dr = argv[1]
# day accuracy dictionary
dacdic = {}
days = []
for file in os.listdir(dr):
	acs, errs, sns, corrs = accuracies(dr + '/' + file)
	aaccs.append(acs)
	aerrs.append(errs)
	asns.append(np.array(sns))
	acorrs.append(np.array(corrs))

	print file, np.max(errs)
	
	aday = file.split('.')[0].split('_')[-1]
	dacdic[aday] = aaccs[-1][80]
	days.append(aday)

days_ord = ['1123', '1124', '1125', '1127', '1129', '1130', '0106', '0107', '0109', '0112', '0226', '0227', '0228', '0301', '0304', '0428', '0429', '0430', '0501', '0502', '0503']
idx = []
for day in days_ord:
	idx.append(days.index(day))
idx = np.array(idx)

aaccs = [aaccs[i] for i in idx]
aerrs = [aerrs[i] for i in idx]
asns = [asns[i] for i in idx]
acorrs = [acorrs[i] for i in idx]

print 'Number of records', len(aaccs)

# plot accuracy / # of spikes day-wise ECDFs
plt.figure()
for i in range(len(aerrs)):
	# for each SN accuracy in windows <=SN
	#print asns[i]
	acdf = []
	snrange = range(50, 300, 5)
	for sn in snrange:
		acdf.append(np.sum(acorrs[i][asns[i] <= sn]) / float(np.sum(asns[i] <= sn)))
	plt.plot(snrange, acdf)

# plot binary classification accuracy for each session
plt.figure()
colors = ['r']*6 + ['b']*4 + ['y']*5 + ['g']*6
for i in range(len(aerrs)):
	acc = aaccs[i][-1]
	plt.bar(i, acc, color=colors[i])
	#plt.errorbar(i+0.4, m, yerr = np.array([[m-h, m+h]]).T, color='black', fmt='.', linewidth=3)
	set_xticks_off()
	set_yticks_font(30)
	plt.xlim(-0.2, 21)
	plt.ylabel('Classification accuracy', fontsize=30)
	plt.subplots_adjust(bottom=0.03, right=0.99, top=0.96)
plt.show()

# plot median error and CI for each session
plt.figure()
colors = ['r']*6 + ['b']*4 + ['y']*5 + ['g']*6
for i in range(len(aerrs)):
	confidence = 0.95
	n = len(aerrs[i])
	a = aerrs[i]
	m, se = np.median(a), scipy.stats.sem(a)
	h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
	print 'MEDIAN and 95% CI', m, m-h, m+h, days[i]
	plt.bar(i, m, color=colors[i])
	plt.errorbar(i+0.4, m, yerr = np.array([[m-h, m+h]]).T, color='black', fmt='.', linewidth=3)
	set_xticks_off()
	set_yticks_font(30)
	plt.ylabel('Median error, cm', fontsize=30)
plt.show()

# accuracy as fucntion of spike number
sn_tot = np.array(sn_tot, dtype=np.float16)
sn_corr = np.array(sn_corr)
sn_acc = sn_corr / sn_tot
sn_bins = np.array(sn_bins)
MINSAM = 20
plt.scatter(sn_bins[sn_tot > MINSAM], sn_acc[sn_tot > MINSAM])
print 'Correlation of total accuracy and number of spikes', pearsonr(sn_bins[sn_tot > MINSAM], sn_acc[sn_tot > MINSAM])
plt.xlabel('Number of spikes', fontsize = LFS)
plt.ylabel('Total accuracy', fontsize = LFS)
plt.grid()
plt.show()

# spike number vs error
totsns = []
toterrs = []
for i in range(len(asns)):
	totsns += asns[i]
	toterrs += aerrs[i]
print 'Correlation of combined errors and spike numbers:', pearsonr(totsns, toterrs)
plt.scatter(totsns, toterrs, s=0.5)
plt.grid()
plt.xlabel('Number of spikes', fontsize=LFS)
plt.ylabel('Decoding error', fontsize=LFS)
plt.show()

# plot cdfs for error
for i in range(len(aerrs)):
	ecdf = smd.ECDF(aerrs[i])
	plt.plot(ecdf.x, ecdf.y)
plt.grid()
LFS = 30
plt.xlabel('Decoding error', fontsize=LFS)
plt.ylabel('CDF', fontsize=LFS)
plt.show()

sumac = []
for i in range(100):
	sumac.append(np.mean([a[i] for a in aaccs]))

plt.figure(figsize = (8, 7))
for ac in aaccs:
	plt.plot(range(100), ac)
plt.plot(range(100), sumac, color = 'black', linewidth = 5)
plt.grid()
lfs = 25
plt.xlabel('Confidence percentile', fontsize = lfs)
plt.ylabel('Accuracy', fontsize = lfs)
set_xticks_font(15)
set_yticks_font(15)
plt.show()

plt.savefig(ld + 'AC_VS_CP.png')

# plot median error from number of spikes
meders = []
meansns = []
days = ['1123', '1124', '1125', '1127', '1130', '1129', '0106', '0107', '0109', '0112', '0226', '0227', '0228', '0301', '0304', '0428', '0429', '0430', '0501', '0502', '0503']

acs80 = []

for path in glob.glob('/home/igor/code/ews/lfp_online/sdl_example/Debug/decer_lin_new/*'):
	if not path.endswith('out') or not 'LIL' in path:
		continue

	for line in open(path):
		if line.startswith('MEDE'):
			meder = float(line.split(' ')[-1])
	fil = path.split('/')[-1]
	animal = fil.split('_')[1]
	day = fil.split('_')[2]

	if not day in days:
		continue

	acs80.append(dacdic[day])

	abpath = '/hdr/data/processing/%s/%s/about.txt' % (animal, day)
	for line in open(abpath):
		if line.startswith('meansn'):
			meansns.append(float(line.split(' ')[-1]))
			meders.append(meder)
			print path, meder

p_acs80 = pearsonr(meansns, acs80)
p_meders = pearsonr(meansns, meders)
print 'Correlation of means and acs80:', np.corrcoef(meansns, acs80)[0,1], 'p=', p_acs80
print 'Correlation of means and meders:', np.corrcoef(meansns, meders)[0,1], 'p=', p_meders

print 'Rank order corrs, means vs acs80:', spearmanr(meansns, acs80)
print 'Rank order corrs, means vs meders:', spearmanr(meansns, meders)

breaka = False

if breaka:
	f, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(9,8))

	# plt.scatter(meansns, meders)
	ax.scatter(meansns, acs80)
	ax2.set_ylim([0, 0.13])
	plt.xlim([50, 200])
	
	ax.set_yticks([0.88, 0.92, 0.96, 1.0])
	ax2.set_yticks([0, 0.04, 0.08, 0.12])

	tfs = 20
	for tick in plt.gca().xaxis.get_major_ticks():
		tick.label.set_fontsize(tfs) 
	for tick in plt.gca().yaxis.get_major_ticks():
		tick.label.set_fontsize(tfs) 
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(tfs) 

	plt.grid()
	ax.grid()

	ax.spines['bottom'].set_visible(False)
	ax2.spines['top'].set_visible(False)
	ax.xaxis.tick_top()
	ax.tick_params(labeltop='off')  # don't put tick labels at the top
	ax2.xaxis.tick_bottom()

	d = .015  # how big to make the diagonal lines in axes coordinates
	# arguments to pass to plot, just so we don't keep repeating them
	kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
	ax.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
	ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

	kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
	ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
	ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

	lfs = 25
	plt.xlabel('Number of spikes', fontsize=lfs)
	# plt.ylabel('Median error')
	plt.ylabel('80% - accuracy', fontsize=lfs)
	ax2.yaxis.set_label_coords(-0.1, 1.0)
	ax.yaxis.set_label_coords(-0.1, 1.0)

	plt.show()
else:
	#f, (ax, ax2) = plt.subplots(2, 1, sharex=True)

	plt.figure(figsize = (9,8))
	#plt.scatter(meansns, meders)
	plt.scatter(meansns, acs80)
	plt.ylim([0, 18])

	print 'Mean accuracy', np.mean(acs80)

	tfs = 20
	for tick in plt.gca().xaxis.get_major_ticks():
		tick.label.set_fontsize(tfs) 
	for tick in plt.gca().yaxis.get_major_ticks():
		tick.label.set_fontsize(tfs) 

	plt.grid()
	lfs = 25
	plt.xlabel('Number of spikes', fontsize=lfs)
	#plt.ylabel('Median error, cm', fontsize=lfs)
	plt.ylabel('80% - accuracy', fontsize=lfs)
	plt.show()
