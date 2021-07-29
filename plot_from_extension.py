#!/usr/bin/env python

# search for files with given extension that contain dictionary 'name - value' and plot specfic values

from sys import argv
from matplotlib import pyplot as plt
import subprocess
import os
import numpy as np
from scipy.stats import wilcoxon
from math import sqrt
from scipy.stats import norm
from call_log import *
from iutils import *
from statsmodels.graphics.gofplots import qqplot
from scipy.stats import shapiro

import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.formula.api import ols

def wilcox(x, y):
	s, p = wilcoxon(x, y)
	return (s,p)

print ''
def bernoulli(x, y):
	X = sum(x)
	n1 = sum(x) + sum(y)
	Y = n1/2
	n2 = n1

	p1 = X / float(n1)
	p2= Y / float(n2)
	p=(X+Y)/float(n1+n2)
	pvalue = 1-norm.sf((p1-p2)/sqrt(p*(1-p)*(1/float(n1) + 1/float(n2))))

	return (1 - pvalue)

if len(argv) < 4:
	print 'Usage: (1)<file name search pattern> (2)<N keys to plot> (3-3+N)<keys to plot> (N+1-M)<dates to include>'
	exit(0)

ld = log_call(argv)

filepat = argv[1]
nkeys = int(argv[2])
keys = argv[3:3+nkeys]

# False => n.s. ANOVA C/T Factor for FTPL => need to transform because of normality assumption
# True => one LOO (wilcox) is n.s. / bootstrap as well! // can test without transform, because bootstrap/wilcoxon does not require normality
# 	... transform only for Anova, but raw test + bootstrap do separately
EPLOG = True
# bootstrapping number of iterations
print 'WARNING: bootsrapping # iterations set to 100 for speed'
NREP = 100

titmap = {'d10' : 'Dwell time',
	'd10_s' : 'Running time within 10 cm of goal',
	'd10_ls' : 'Dwell time, 10 cm, low speed',
	'trg' : 'Time to reach the goal',
	'trgl' : 'Time to reach the goal (new learning)',
	'nc10' : 'Number of crossings',
	'prg' : 'Path to reach the goal',
	'ftpl' : 'Excess path length' }#+ (', log' if EPLOG else '')} # , cm
	#'ftpl' : 'Excess path' + (', log' if EPLOG else '')}

unitmap = {'ftpl' : 'Normalized\npath length',
	   'd10'  : 'Normalized time near goal',
	   'nc10' : 'Number of crossings'}

tests = {'d10' : wilcox,
	 'nc10' : wilcox, # bernoulli
	'ftpl' : wilcox,
	'd10_s' : wilcox,
	'd10_ls' : wilcox,
	'prg' : wilcox,
	'trg' : wilcox,
	'trgl' : wilcox}

flist = subprocess.check_output(['find', '.', '-name', filepat])
print flist

valid_dates = argv[3+nkeys:]
print 'Valid dates: ', str(valid_dates)

dlist = []
vlist = []
# animals list
alist = []

for i in range(nkeys):
	vlist.append([[], []])

for fpath in flist.split('\n'):
	if len(fpath) == 0:
		continue

	log_file(ld, fpath)

	newdate = '-'
	fab = os.path.dirname(fpath) + '/../about.txt'
	for l in open(fab):
		wsa = l.split(' ')
		if wsa[0] == 'date':
			newdate = wsa[1][:-1]
		if wsa[0] == 'animal':
			newanimal = wsa[1][:-1]
	
	if newdate == '-':
		print 'NO DATE IN FILE ', fpath, ', EXIT'
		exit(1)

	if newdate not in valid_dates:
		print 'Skip date<%s>' % newdate
		print 'len: ', str(len(newdate))
		continue

	for line in open(fpath):
		ws = line.split(' ')
		if len(ws) < 2:
			continue

		if ws[0] in keys:
			newval = float(ws[1])
			newval2 = float(ws[2])	

			#if ws[0] == 'd10':
			#	print 'WARNING: scale d10'
			#	newval *= 180
			#	newval2 *= 180

			vlist[keys.index(ws[0])][0].append(newval)
			vlist[keys.index(ws[0])][1].append(newval2)

	# insert into the list with new date value

	#di = 0
	#while di < len(dlist) and dlist[di] < newdate:
	#	di += 1
	#dlist.insert(di, newdate)

	dlist.append(newdate)
	alist.append(newanimal)

	# vlist.insert(di, newval)

print 'Number of dates / animal entries: %d / %d' % (len(dlist), len(alist))

print 'Sort dlist...'
sorti = np.argsort(dlist)
dlist = sorted(dlist)
for i in range(nkeys):
	vlist[i][0] = [vlist[i][0][s] for s in sorti]
	vlist[i][1] = [vlist[i][1][s] for s in sorti]
alist = [alist[s] for s in sorti]

# DEBUG - QQPLOT
#for i in range(nkeys):
#	qqplot(np.array(vlist[i][0]), line='s')
#	plt.show()
#	qqplot(np.array(vlist[i][1]), line='s')
#	plt.show()

alistu = list(set(alist))
cols = ['b', 'r', 'g', 'y']
acoldic = dict(zip(alistu, cols[:len(alistu)]))
print acoldic

print 'Unique animal list: ', alistu

acollist = []
for a in alist:
	acollist.append(acoldic[a])

print 'Animal colours: ', str(acollist)

bars = [[], []]
stds = [[], []]

# f, ax = plt.figure()
N = len(vlist[0][0])
barx = np.array(range(N))

# means / stds of all measures
vmeans = []
vstds = []
for k in range(nkeys): 
	vmeans.append(np.mean(vlist[k][0] + vlist[k][1]))
	vstds.append(np.std(vlist[k][0] + vlist[k][1]))

# average of 3 measures
combvals = [[0] * len(vlist[0][0]), [0] * len(vlist[0][0])]
dsums = [0]* len(vlist[0][0])
for k in range(nkeys):
	for i in range(len(vlist[0][0])):
		#print k, i
		if keys[k] == 'ftpl' or keys[k] == 'trgl' or keys[k] == 'prg' or keys[k] == 'trg':
			combvals[0][i] += 0.5 * (vlist[k][1][i] - vmeans[k]) / vstds[k]
			combvals[1][i] += 0.5 * (vlist[k][0][i] - vmeans[k]) / vstds[k]
			
			dsums[i] += 0.5 * ((vlist[k][1][i] - vlist[k][0][i]) / float(vlist[k][0][i] + vlist[k][1][i]))
		else:
			combvals[0][i] += 0.25 * (vlist[k][0][i] - vmeans[k]) / vstds[k]
			combvals[1][i] += 0.25 * (vlist[k][1][i] - vmeans[k]) / vstds[k]

			s = vlist[k][0][i] + vlist[k][1][i]
			if s == 0:
				s=1
			dsums[i] += 0.25 * (vlist[k][0][i] - vlist[k][1][i])/ float(s)
dsums = [d/3 for d in dsums]
print dsums

# animal means - [animal][con/targ]
ameans = np.zeros((3, 4, 2))
astds =  np.zeros((3, 4, 2))

#PSC = 54.0
#printTrueNING: RESCALE FTPL'
#bars[0][2] /= PSC
#bars[1][2] /= PSC
#stds[0][2] /= PSC
#stds[1][2] /= PSC
#for k in range(len(vlist[2][0])):
#	vlist[2][0][k] /= PSC
#	vlist[2][1][k] /= PSC

for i in range(len(keys)):
	key = keys[i]
	# plt.plot(range(len(vlist[0][0])), vlist[i], lw=3)

	plt.figure(figsize=(10,7))

	# bars
	#plt.bar(barx, vlist[i][0], width=0.2)
	#plt.bar(barx+0.3, vlist[i][1], width=0.2, color='r')

	# LGO HERE
	if EPLOG and key == 'ftpl':
		vlist[i][0] = [np.log(v) for v in vlist[i][0]]
		vlist[i][1] = [np.log(v) for v in vlist[i][1]]

	# DEBUG !
	#print 'WARNING: data transformed in the debug mode'	
	#vlist[i][0] = [1/v if v > 0 else 0 for v in vlist[i][0]]
	#vlist[i][1] = [1/v if v > 0 else 0 for v in vlist[i][1]]

	sh1, psh1 = shapiro(vlist[i][0])
	sh2, psh2 = shapiro(vlist[i][1])
	print 'SHAPIRO TEST RESUTS (P<=alpha => not normal):', psh1, psh2

	# one by sum
	if key == 'ftpl' or key == 'trgl' or key == 'prg' or key == 'trg':
		sm = [(vlist[i][1][k] - vlist[i][0][k])/float(vlist[i][1][k] + vlist[i][0][k]) for k in range(len(vlist[i][0]))]
	#elif key == 'nc10':
	#	sm = [(vlist[i][0][k] - vlist[i][1][k]) for k in range(len(vlist[i][0]))]
	else:
		sm = [(vlist[i][0][k] - vlist[i][1][k])/float(vlist[i][1][k] + vlist[i][0][k]) for k in range(len(vlist[i][0]))]

	# for combined behavioural score	
	# sm = dsums
	
	h = plt.scatter(barx, sm, lw=6, color = acollist)
	plt.legend(handles = [h])
	plt.axhline(y=0.0, lw=3, color='black')

	# animal means
	rs = [0,6,10,15,21]
	rcols = ['r', 'b', 'y', 'g']
	for j in range(1,5):
		amean = np.mean(sm[rs[j-1]:rs[j]])
		ameans[i][j-1][0] = np.mean(vlist[i][0][rs[j-1]:rs[j]])
		ameans[i][j-1][1] = np.mean(vlist[i][1][rs[j-1]:rs[j]])
		astds[i][j-1][0] = np.std(vlist[i][0][rs[j-1]:rs[j]]) / np.sqrt(rs[j] - rs[j-1])
		astds[i][j-1][1] = np.std(vlist[i][1][rs[j-1]:rs[j]]) / np.sqrt(rs[j] - rs[j-1])
		plt.plot([rs[j-1], rs[j]-1], [amean, amean], linewidth = 3, color = rcols[j-1])

		#if keys[i] == 'ftpl':
			#ameans[i][j-1][0] = np.log(ameans[i][j-1][0])
			#ameans[i][j-1][1] = np.log(ameans[i][j-1][1])
			#astds[i][j-1][0] = np.log(astds[i][j-1][0])
			#astds[i][j-1][1] = np.log(astds[i][j-1][1])

	axes = plt.gca()

	#if key != 'nc10':
	axes.set_ylim([-1.05, 1.05])
	#axes.set_ylim([-0.3, 0.3])

	#plt.xticks(barx, dlist, rotation='vertical')
	#plt.xticks(barx, [''] * len(barx), rotation='vertical')
	plt.xticks([],[])
	#plt.grid()
	axes.set_xlim([-1, N])

	axes.tick_params(labelsize = 20)

	plt.xlabel('Session', fontsize=45)
	#plt.ylabel('Behavioural score', fontsize=45)
	plt.ylabel('Relative change', fontsize=45)
	set_yticks_font(35)

	# axes.get_xaxis().set_visible(False)

	tres = 'P-value RAW COMPARE: %.4f, %.4f' % tests[key](vlist[i][0], vlist[i][1])	
	atres = 'leave-1-out: '

	print tres

	# animal-wise tests:
	loos = []
	for a in alistu:
		xa = [vlist[i][0][j] for j in range(N) if alist[j] != a]
		ya = [vlist[i][1][j] for j in range(N) if alist[j] != a]
		#xa = [combvals[0][j] for j in range(N) if alist[j] != a]
		#ya = [combvals[1][j] for j in range(N) if alist[j] != a]

		atres += '%.4f' % tests[key](xa, ya)[1] + ' '
		loos.append(wilcox(xa, ya))

		# bootsrap loo
		loosc = [(vlist[i][0][j] - vlist[i][1][j]) / float(vlist[i][0][j] + vlist[i][1][j]) for j in range(N) if alist[j] != a]
		smeans = []
		for tmpi in range(NREP):
			smeans.append(np.median(np.random.choice(loosc, len(loosc))))
		smeans_sort = np.array(sorted(smeans))
		print 'BOOTSTRAPPED LOO/%s 95%% %s : %.2f-%.2f' % (a, keys[i], smeans_sort[NREP/20], smeans_sort[NREP*19/20]), 'p-value: ', float(np.sum(smeans_sort < 0))/len(smeans_sort)

		#t = 0
		#while smeans_sort[t] < 0:
		#	t += 1
		#print 'cross 0 at: ', t / 10000.0

	print 'WILCOX LOO:', loos

	#plt.title('Combined score, 3 measures\n%s\n%s'% (tres, atres)
	# plt.title(titmap[key] + '\n' + tres + '\n' + atres)
	plt.title(titmap[key], fontsize = 40)
	plt.subplots_adjust(left=0.16)

	#plt.title(titmap[key], fontsize = 30)# + '\n' + atres)
	#pv = wilcox(combvals[0], combvals[1])

	#plt.title('Combined behavioural score, p-value = %.3f\n leave-1-out p-values: %.3f/%.3f/%.3f/%.3f ' % (pv, loos[0], loos[1], loos[2], loos[3]), fontsize = 20)

	plt.savefig(ld + key + '.png')
	plt.show()

	bars[0].append(np.mean(vlist[i][0]))
	bars[1].append(np.mean(vlist[i][1]))
	
	stds[0].append(np.std(vlist[i][0]) / sqrt(N))
	stds[1].append(np.std(vlist[i][1]) / sqrt(N))

# 2-way anova
# form a data frame
for m in range(len(vlist)):
	print 'Perform 2-way ANOVA for ', keys[m]
	d = {'beh':vlist[m][0] + vlist[m][1], 'ct':[0]*len(dlist) + [1]*len(dlist), 'an':alist + alist}
	df = pd.DataFrame(data=d)
	formula = 'beh ~ C(ct) + C(an) + C(ct):C(an)'
	#formula = 'beh ~ C(ct) + C(an)'
	model = ols(formula, df).fit()
	aov_table = statsmodels.stats.anova.anova_lm(model, typ=2)
	print(aov_table)

#print 'WARNING: RESCALE D10'
#bars[0][0] *= 2000
#bars[1][0] *= 2000
#stds[0][0] *= 2000
#stds[1][0] *= 2000

#print 'WARNING: RESCALE FTPL'
#bars[0][2] /= PSC
#bars[1][2] /= PSC
#stds[0][2] /= PSC
#stds[1][2] /= PSC
#for k in range(len(vlist[2][0])):
#	vlist[2][0][k] /= PSC
#	vlist[2][1][k] /= PSC

#s2 = 93.82
#bars[0][2] /= s2
#bars[1][2] /= s2
#stds[0][2] /= s2
#stds[1][2] /= s2

print bars[0][2], bars[1][2]

#plt.figure(figsize=(12,4))
# lines per day - con to targ, bold for correct, color per animal
f, axarr = plt.subplots(1, len(keys), figsize=(22, 5))
for j in range(len(keys)):
	for a in range(4):
		for ad in range(rs[a],rs[a+1]):
			lw = 5 if (vlist[j][0][ad] > vlist[j][1][ad]) ^ (keys[j] == 'ftpl') else 2
			axarr[j].plot([0, 1], [vlist[j][0][ad], vlist[j][1][ad]], color=cols[a], linewidth = lw)
			#axarr[j].set_xlabel(titmap[keys[j]])

			axarr[j].set_xticks([0, 1])
			#axarr[j].set_xticklabels(['CONTROL', 'TARGET'], rotation='vertical', fontsize=30)
			axarr[j].set_xticklabels(['Control', 'Target'], fontsize=30)
			#plt.xticks([0,1], ['CONTROL', 'TARGET'], rotation='vertical')

			axarr[j].set_xlim([-0.3, 1.3])

			axarr[j].set_ylabel(titmap[keys[j]], fontsize=30)
			
			axarr[j].yaxis.set_ticks_position('left')
			axarr[j].xaxis.set_ticks_position('bottom')

			plt.sca(axarr[j])
			set_yticks_font(30)

plt.subplots_adjust(bottom=0.09, right=0.99, top=0.95, left=0.08)
axarr[-1].set_yscale("log")
axarr[-1].set_ylim([-0.5, 52])
axarr[-2].set_ylim([0, 10])

plt.show()

# PLOT MEAN SCORE BARS
f, axarr = plt.subplots(1, len(keys))
btit = ['Dwell time', 'Number of\ncrossings', 'Normalized\npath length']
for j in range(len(keys)):        
	if keys[j] == 'ftpl' or keys[j] == 'trgl' or keys[j] == 'prg' or keys[j] == 'trg':
       		sm = [(vlist[j][1][k] - vlist[j][0][k])/float(vlist[j][1][k] + vlist[j][0][k]) for k in range(len(vlist[j][0]))]
        else:
	        sm = [(vlist[j][0][k] - vlist[j][1][k])/float(vlist[j][1][k] + vlist[j][0][k]) for k in range(len(vlist[j][0]))]
	axarr[j].bar(0, np.mean(sm), width = 0.2)
	axarr[j].errorbar(0.1, np.mean(sm), np.std(sm) / sqrt(N), linewidth = 3, color = 'black')
	axarr[j].set_xlim([-0.3, 0.5])
	axarr[j].get_xaxis().set_visible(False)
	axarr[j].tick_params(labelsize = 20)
	axarr[j].set_title(btit[j], fontsize=25)

	# bootstrap scores
	smeans = []
	for i in range(NREP):
		smeans.append(np.mean(np.random.choice(sm, len(sm))))
	smeans_sort = sorted(smeans)

	t = 0
	while smeans_sort[t] < 0:
		t += 1
	print 'cross 0 at: ', t / float(NREP)

	print 'BOOTSTRAPPED 95%% %s : %.2f-%.2f' % (keys[j], smeans_sort[NREP/20], smeans_sort[NREP*19/20])

plt.show()

DIFF = False
# or animal - wise
TOTAL = False

# plot bars
print 'Plot bars'
f, axarr = plt.subplots(1, len(keys))
barx = np.array(range(len(bars[0])))
for i in range(len(keys)):
	# total
	if TOTAL:
		axarr[i].bar(0, bars[0][i], width = 0.2)
		axarr[i].bar(0.5, bars[1][i], width = 0.2, color = 'r')
		#axarr[i].legend(['Control', 'Target'], loc='best', fontsize=15)
		axarr[i].legend(['Control', 'Target'], loc='best', fontsize=20)

		# total only
		axarr[i].errorbar(0.1, bars[0][i], yerr=stds[0][i], linewidth = 3, color = 'black')
		axarr[i].errorbar(0.6, bars[1][i], yerr=stds[1][i], color = 'black', linewidth = 3)
	else:
		# animal-wise
		bx = np.array([0, 1, 2, 3])

		if not DIFF:
			axarr[i].bar(bx, ameans[i,:,0], width = 0.2, alpha = 0.6)
			axarr[i].bar(bx + 0.5, ameans[i,:,1], width = 0.2, color = 'r')
			axarr[i].legend(['Control', 'Target'], loc='best', fontsize=20)
		else:
			axarr[i].bar(bx, ameans[i,:,1] - ameans[i,:,0], width = 0.2, alpha = 0.6)

		for j in range(4):
			l = len(vlist[i][0][rs[j]:rs[j+1]])
			if not DIFF:
				axarr[i].scatter([bx[j] + 0.1] * l, 	    vlist[i][0][rs[j]:rs[j+1]], color='black',zorder=10)	
				axarr[i].scatter([bx[j] + 0.6] * l, vlist[i][1][rs[j]:rs[j+1]], color='black', zorder=10)
			else:
				axarr[i].scatter([bx[j] + 0.1] * l, np.array(vlist[i][1][rs[j]:rs[j+1]]) - np.array(vlist[i][0][rs[j]:rs[j+1]]), color='black',zorder=10)	

		# animal-wise
		if not DIFF:
			axarr[i].errorbar(bx + 0.1, ameans[i,:,0], yerr=astds[i,:,0], linewidth = 3, color = 'black', fmt='o')
			axarr[i].errorbar(bx + 0.6, ameans[i,:,1], yerr=astds[i,:,1], color = 'black', linewidth = 3, fmt='o')

	axarr[i].set_title(titmap[keys[i]], fontsize = 25)
	#axarr[i].set_xticks([0], [titmap[keys[i]]])

	# axarr[i].set_xlabel(unitmap[keys[i]])
	axarr[i].xaxis.set_major_locator(plt.NullLocator())
	#if keys[i] == 'ftpl':
	#	axarr[i].set_ylim([0, 1050])
	
	if not DIFF : # and keys[i] != 'ftpl':
		#axarr[i].set_ylim([0, max(vlist[i][0] + vlist[i][1]) * 1.01])
		if TOTAL:
			axarr[i].set_ylim([0, max(bars[0][i] + stds[0][i], bars[1][i] + stds[1][i]) * 1.4])
		else:
			axarr[i].set_ylim([0, max(vlist[i][0] + vlist[i][1]) * 1.1])
	
	axarr[i].tick_params(labelsize = 20)
	# axarr[i].yaxis.set_label_position("right")

# plt.xticks(barx, keys)
plt.show()
