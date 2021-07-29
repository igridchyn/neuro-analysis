#!/usr/bin/env python2

from sys import argv
import numpy as np
import os
from iutils import *
from matplotlib import pyplot as plt
from call_log import *

def read_lists(path):
	flcpre = open(path)
	n1 = int(flcpre.readline())
	l1 = [float(flcpre.readline()) for i in range(n1)]
	n2 = int(flcpre.readline())
	l2 = [float(flcpre.readline()) for i in range(n2)]

	return l1, l2

def plot_mean(lcs, col, split, start, MAXL):
	#MAXL = max([len(lcs[i]) for i in range(len(lcs))])
	print 'WARINING: max length limited to', MAXL
	mlc = []
	# standard error of the mean
	slc = []
	for i in range(MAXL):
		trlist = [lcs[j][i] for j in range(len(lcs)) if (len(lcs[j]) > i and lcs[j][i] > 0)]
		dat = np.mean(trlist)
		mlc.append(dat / 1000)
		sem = np.std(trlist) / np.sqrt(len(trlist))
		slc.append(sem / 1000)
		
	rng = range(1+start, len(mlc) + 1+start)

	mh, = plt.plot(rng[:split], mlc[:split], color = col, linewidth = 4)
	plt.plot(rng[split:], mlc[split:], color = col, linewidth = 4)

	plt.errorbar(rng, mlc, slc, color='black',  fmt='.', linewidth = 2)

	return mh

NARG = 2
if len(argv) < NARG:
	print 'USAGE: (1)<list of directories>'
	exit(0)

ld = log_call(argv)

# learning curves pre/post
lcs_pre  = [[],[]]
lcs_post = [[],[]]

# rev4 - RATIO, rev5 - ABSOLUTE
REV = '.rev5'

FDLIST = argv[1]
CWD =  os.getcwd()
for line in open(FDLIST):
	if len(line) < 2:
		print 'WARNING: skip line', line
		continue

	os.chdir('/hdr/data/processing/' + line[:-1])
	vrs = resolve_vars(['%{animal}','%{day}','%{FULL}', '%{swap}'])
	[animal, day, full, swap] = vrs
	swap = int(swap)
	
	print os.getcwd(), full
	plc_pre = '9l%s/%s_%s_9l.whl.learning%s' % (full, animal, day, REV)
	l1, l2 = read_lists(plc_pre)

	lcs_pre[swap].append(l1)
	lcs_pre[1-swap].append(l2)

	plc_post = '16l%s/%s_%s_16l.whl.learning%s' % (full, animal, day, REV)
	l1, l2 = read_lists(plc_post)

	lcs_post[swap].append(l1)
	lcs_post[1-swap].append(l2)

print '7th (1-based) trials target:', [lc[6] for lc in lcs_pre[1]]
print '7th (1-based) trials control:', [lc[6] for lc in lcs_pre[0]]

# plot average learning curves
# ... break, start at, maxl

#plt.figure(figsize = (12, 10))
plt.figure(figsize = (10, 8))

#mhpre1 = plot_mean(lcs_pre[0], 'blue', 6, 0, 11)
#mhpre2 = plot_mean(lcs_pre[1], 'red' , 6, 0, 11)

mhpost1 = plot_mean(lcs_post[0], 'blue', 5, 11, 10) # was start 1 # was green
mhpost2 = plot_mean(lcs_post[1], 'red', 5, 11, 10) # was start 1 # was brown

# plt.grid()
#plt.legend([mhpre1, mhpre2, mhpost1, mhpost2], ['CONTROL', 'TARGET', 'CONTROL, POST-LEARNING', 'TARGET, POST-LEARNING'], fontsize=25)
#plt.legend([mhpre1, mhpre2, mhpost1, mhpost2], ['Control', 'Target'], fontsize=25)

#plt.legend([mhpre1, mhpre2], ['Control', 'Target'], fontsize=25)
plt.legend([mhpost1, mhpost2], ['Control', 'Target'], fontsize=25)

#plt.xticks([4,9,14,19], ['LEARNING 1', 'LEARNING 2', 'POST-LEARNING 1', 'POST-LEARNING 2'], fontsize=25, rotation=34)
plt.xticks([], [])

#plt.text(3, 500, 'A', fontsize=30)
#plt.text(8, 500, 'B', fontsize=30)
#plt.text(13, 500, 'C', fontsize=30)
#plt.text(18, 500, 'D', fontsize=30)
set_yticks_font(25)
plt.subplots_adjust(bottom=0.05)
plt.ylabel('Excess path length, m', fontsize=34)
#plt.subplots_adjust(left=0.13)

plt.tight_layout()
plt.subplots_adjust(left=0.16)

plt.gca().set_yscale('log')

strip_axes(plt.gca())

plt.show()
