#!/usr/bin/env python

import os
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from iutils import *
from scipy.stats import ttest_rel, ttest_ind, wilcoxon
from math import sqrt

def npexp(a):
	return a

if len(argv) < 5:
	print 'USAGE: (1)<file with list of direcotires> (2)<file with *redyn output> (3)<0/1  : CONF MODE (for label only)> (4)<normalized values to sum up to 1>'
	exit(0)

NORM1 = int(argv[4])

dirs = []
for line in open(argv[1]):
	dirs.append(line[:-1])
# dirs = dirs[:-1]

CONF = bool(int(argv[3]))

fname = argv[2]

NF = 6
vals = []
# first - contol, second = target
# before / after
for i in range(NF):
	vals.append([[], []])

for dr in dirs:
	f = open(dr + '/' + fname)

        # swap
        apath = dr + '/../about.txt'
        for line in open(apath):
                if line.startswith('swap'):
                        swap = (bool(int(line.split(' ')[-1])))

	f.readline()
	# incides of control / target
	i1 = 1 - swap
	i2 = int(swap)
	#it = 0
	#ic = 1

	print 'Indices of 1st/2nd line: ', i1, i2, 'Swap ', swap

	# |L1 > L2|, |L2 > L1| : before and after
	svb = [float(w) for w in f.readline().split(' ')]
	sva = [float(w) for w in f.readline().split(' ')]
	print svb, sva
	# now below - correaltions
	#vals[0][0].append(svb[swap])
	#vals[0][1].append(sva[swap])
	
	f.readline() # skip line 4
	# difference before ... 
	c1 = float(f.readline())
	# difference after ...
	c2 = float(f.readline())
	# mean confidence ... mean(L1-L2)
	if swap:
		vals[1][0].append(-c1)
		vals[1][1].append(-c2)
	else:
		vals[1][0].append(c1)
		vals[1][1].append(c2)
		
	f.readline() # 7
	sv1 = [float(w) for w in f.readline().split(' ')]
	sv2 = [float(w) for w in f.readline().split(' ')]
	# l1-l2
	#vals[2][i1].append(sv2[0]-sv1[0])
	#vals[2][i2].append(sv2[1]-sv1[1])

	# CON : Lik before, Lik after
	#vals[1][0].append(sv1[i1]) # CON before
	#vals[1][1].append(sv2[i1]) # CON after
	#  TARG : Lik before, Lik after
	#vals[0][0].append(sv1[i2]) # TARG BEFORE
	#vals[0][1].append(sv2[i2]) # TARG AFTER

	# !! 23.01
	# BEFORE : CON / TARG
	#vals[1][0].append(sv1[i1]) # CON before
	#vals[1][1].append(sv1[i2]) # TARG before
	# AFTER : CON / TARG
	#vals[0][0].append(sv2[i1]) # CON after
	#vals[0][1].append(sv2[i2]) # TARG after

	# correlations - first values
	sv = [float(w) for w in f.readline().split(' ')]
	#vals[0][1-swap].append(sv[0])
	#vals[0][swap].append(sv[1])

	# ratio of meaningful - before and after
	sv1 = [float(w) for w in f.readline().split(' ') if len(w) > 1]
	sv2 = [float(w) for w in f.readline().split(' ') if len(w) > 1]
	svs = [sv1, sv2]
	# thold indx
	#thid = 9
	ten = range(1, 10)
	vals[3][i1].append([np.log(svs[swap][thid] / svs[1-swap][thid])  if svs[1-swap][thid] > 0 and svs[swap][thid] > 0 else np.nan for thid in ten])
	vals[3][i2].append([np.log(svs[swap][10 + thid] / svs[1-swap][10 + thid]) if svs[1-swap][10 + thid] and svs[swap][10 + thid] > 0 else np.nan for thid in ten])
	# percentage significant : before, after, [4]-control, [5]-trarget
	vals[5-swap][0].append(sv1[1:10]) # thid
	vals[5-swap][1].append(sv1[11:]) # thid + 10
	vals[4+swap][0].append(sv2[1:10])
	vals[4+swap][1].append(sv2[11:])

	# total probs - 2 values
	totp = [float(w) for w in f.readline().split(' ')]
	vals[2][0].append(totp[0])
	vals[2][1].append(totp[1])

# SINGLE
vals[1][0] = np.array(vals[1][0])
vals[1][1] = np.array(vals[1][1])
vals[0][0] = np.array(vals[0][0])
vals[0][1] = np.array(vals[0][1])
plt.figure()
bw = 0.27 # 0.07 for individual
ln = len(vals[0][0])

# every day
#plt.bar([i for i in range(ln)], npexp(vals[1][0]), width = bw)
#plt.bar([i+bw*2 for i in range(ln)], npexp(vals[1][1]), width = bw, color='red')
#plt.bar([i+bw*4 for i in range(ln)], npexp(vals[0][0]), width = bw, color='green')
#plt.bar([i+bw*6 for i in range(ln)], npexp(vals[0][1]), width = bw, color='black')

print 'WARNING: values normalized to sum up to 1'
if NORM1:
	for i in range(ln):
		sm1 = vals[1][0] + vals[1][1]
		sm2 = vals[0][0] + vals[0][1]
		vals[1][0] /= sm1
		vals[1][1] /= sm1
		vals[0][0] /= sm2
		vals[0][1] /= sm2

# means
plt.bar([0], np.mean(npexp(vals[1][0])), width = bw)
plt.bar([1], np.mean(npexp(vals[1][1])), width = bw, color='red')
plt.bar([2], np.mean(npexp(vals[0][0])), width = bw, color='green')
plt.bar([3], np.mean(npexp(vals[0][1])), width = bw, color='brown')
plt.legend(['CONTROL BEFORE', 'TARGET BEFORE', 'CONTROL AFTER', 'TARGET AFTER'])
plt.errorbar([0+bw/2], np.mean(npexp(vals[1][0])), yerr=np.std(npexp(vals[1][0]))/np.sqrt(ln), color = 'black', linewidth=4)
plt.errorbar([1+bw/2], np.mean(npexp(vals[1][1])), yerr=np.std(npexp(vals[1][1]))/np.sqrt(ln), color = 'black', linewidth=4)
plt.errorbar([2+bw/2], np.mean(npexp(vals[0][0])), yerr=np.std(npexp(vals[0][0]))/np.sqrt(ln), color = 'black', linewidth=4)
plt.errorbar([3+bw/2], np.mean(npexp(vals[0][1])), yerr=np.std(npexp(vals[0][1]))/np.sqrt(ln), color = 'black', linewidth=4)
plt.xticks([], [])

plt.title(argv[2], fontsize = 25)
plt.show()
exit(0)

#=======================================================================================================================================

print '%d ENTRIES' % len(vals[0][0])

# DEBUG
print  vals[3]

# last 3 are: index and THRESHOLD (CONF/LIK) DEPENDENT
# 1 : 'TARG > CON: before and after'
pclabs = [['Percentage L_CON > Z_THOLD', 'Percentage :L_TARG > Z_THOLD'], ['Percentage L_CON - L_TARG > Z_THOLD', 'Percentage L_TARG - L_CON > Z_THOLD']]

# labels = ['Correlations of before and after', 'Mean L_TARG-L_CON: before and after', 'Likelihood drop: control vs. target', 'LOG(|SIG_TARG|/|SIG_CON|): before and after ', pclabs[CONF][0], pclabs[CONF][1]]
labels = ['BEFORE PROBS', 'AFTER PROBS', 'TOTAL PROBS', 'LOG(|SIG_TARG|/|SIG_CON|)', pclabs[CONF][0], pclabs[CONF][1]]

baleg = ['BEFORE', 'AFTER']
ctleg = ['CONTROL', 'TARGET']
legends = [ctleg, ctleg, baleg, baleg, baleg, baleg]

figb, ((ax1b, ax2b, ax3b), (ax4b, ax5b, ax6b)) = plt.subplots(2,3, figsize=(22, 12))
axarrb = [ax1b, ax2b, ax3b, ax4b, ax5b, ax6b]
pstr=[''] * NF
pi = 0
bw = 0.2

# plot
for i in range(NF):
	# PSOPT
	SESWISE = True

	# NORMAL
	if i < 3 and not SESWISE:	
		v1a = [vals[i][0]]
		v2a = [vals[i][1]]
	else:
		v1a = vals[i][0]
		v2a = vals[i][1]
	# (DIFF)/(SUM)
	#v1 = (vals[1][0]-vals[0][0])/(vals[1][0]+vals[0][0])
	#v2 = (vals[1][1]-vals[0][1])/(vals[1][1]+vals[0][1])
	LRANGE = range(1) if i < 3 else range(len(v1a[0]))
	if SESWISE and i < 3:
		LRANGE = range(len(v1a))

	for pi in LRANGE:
		if i < 3:
			if not SESWISE:
				v1 = np.array(v1a[pi])
				v2 = np.array(v2a[pi])
			else:
				v1 = np.array([v1a[pi]])
				v2 = np.array([v2a[pi]])
		else:
			v1 = np.array([v1a[j][pi] for j in range(len(v1a)) if ~np.isnan(v1a[j][pi]) and ~np.isnan(v2a[j][pi])])
			v2 = np.array([v2a[j][pi] for j in range(len(v2a)) if ~np.isnan(v1a[j][pi]) and ~np.isnan(v1a[j][pi])])
			
		ind1 = ~np.isnan(v1)
		ind2 = ~np.isnan(v2)
		if sum(ind1) > 0 and sum(ind2) > 0:
			p=ttest_ind(v1[ind1], v2[ind2])[1]
			pstr[i] += '%.2f '%p
		else:
			p = 0
		pw = 0 #if i > 0 else wilcoxon(v1[ind1], v2[ind2])[1]

		axarrb[i].set_title(labels[i] + '\n%.5f' % p )
		axarrb[i].bar([2*pi], [np.mean(v1[ind1])], width = bw)
		axarrb[i].bar([2*pi+0.7], [np.mean(v2[ind2])], width = bw, color='r')

		if pi == 0:
			axarrb[i].legend(legends[i], loc='best')
		axarrb[i].errorbar([2*pi+bw/2], [np.mean(v1[ind1])], yerr=[np.std(v1[ind1])/sqrt(sum(ind1))], color='black', linewidth=3)
		axarrb[i].errorbar([2*pi+0.7+bw/2], [np.mean(v2[ind2])], yerr=[np.std(v2[ind2])/sqrt(sum(ind2))], color='black', linewidth=3)

		plt.sca(axarrb[i])
		nfs = 15
		#plt.text(2*pi, np.mean(v1[ind1])/2, str(sum(ind1)), fontsize=nfs, color='green')
		#plt.text(2*pi+0.7, np.mean(v2[ind2])/2, str(sum(ind2)), fontsize=nfs, color='green')

plt.tight_layout()
plt.suptitle(argv[2], fontsize = 20)
plt.show()
