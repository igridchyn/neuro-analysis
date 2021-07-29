#!/usr/bin/env python2

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
from call_log import *
from iutils import *
import re

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'


def p_to_sig_str(p):
	if p > 0.1:
		return 'n.s.'
	elif p > 0.05:
		return '^'
	elif p > 0.01:
		return '*'
	elif p > 0.005:
		return '**'
	elif p > 0.001:
		return '***'
	else:
		return '****'

suppress_warnings()

if len(argv) < 6:
	print 'USAGE: (1)<pfs stats output> (2)<title> (3)<measure> (4)<#session 1> (5)<#session2>'
	print 'Plot stat output of pfs_summary - assuming that 4 ouputs are merged in a single file'
	exit(0)

ld = log_call(argv)
log_file(ld, argv[1])

#snames = ['', 'L1-START', 'L1-END', 'POST', 'L2-START', 'L2-END']
#snames = ['', 'START OF LEARNING', 'END OF LEARNING', 'POST-PROBE', 'START OF POST-LEARNING', 'END OF POST-LEARNING']
#snames = ['', 'Start of learning', 'End of learning', 'Post-probe', 'Start of post-learning', 'End of post-learning']
snames = ['', '1st learning trial', 'End of learning', 'Probe', '1st post-learning trial', 'End of post-learning']

s1name = snames[int(argv[4])]
s2name = snames[int(argv[5])]

s1 = int(argv[4])
s2 = int(argv[5])

#TIT =  '%s VS. %s, %s' % (s1name, s2name, argv[2])
TIT=argv[2]
# format: mean std n mean std n p_ks p_mw

f = open(argv[1])
meas = int(argv[3]) # 8 in total

# mean / std / n
valm = [[],[]] # con, mut
vals = [[],[]]
valn = [[],[]]
p_mw = []
p_ks = []
p_mw_s = []

# all inh disinh unaff
for i in range(4):
	# params
	f.readline()
	# skip measures
	for i in range(meas):
		f.readline()
	mline = f.readline()
	lv = [float(w) for w in mline.split(' ')]

	valm[1].append(lv[0])
	valm[0].append(lv[3])
	vals[1].append(lv[1])
	vals[0].append(lv[4])
	valn[1].append(lv[2])
	valn[0].append(lv[5])

	p_ks.append(lv[6])
	p_mw.append(lv[7])
	p_mw_s.append(lv[8])

	# skip rest of values
	for i in range(8-meas-1):
		f.readline()

# plot 4 pairs of bars

#CATEG_LABS = ['ALL', 'INHIBITED', 'DISINHIBITED', 'UNAFFECTED']
CATEG_LABS = ['All', 'Inhibited', 'Disinhibited', 'Unafected']

p_ks = np.array(p_ks)
p_mw = np.array(p_mw)

# correct last 3 p-values for multiple testing
print 'WARINING: p-values corrected for multiple testing'
print 'Before correction: ', p_ks
print 'Before correction (MW): ', p_mw

# 3 values
#pord = np.argsort(p_ks[1:])
#p_ks[1:][pord] *= [3,2,1]
#pord = np.argsort(p_mw[1:])
#p_mw[1:][pord] *= [3,2,1]

# 2 comparisons
#print 'WARNING: 2 comparisons MULTIPLE TESTING ASSUMED'
#pord = np.argsort(p_ks[1:3])
#p_ks[1:3][pord] *= [2,1]
#pord = np.argsort(p_mw[1:3])
#p_mw[1:3][pord] *= [2,1]

print 'WARNING: NO MULTIPLE TESTING CORRECTION'

print 'After correction: ', p_ks
print 'After correction (MW): ', p_mw
print '... Satistic values:', p_mw_s

print 'Data size: C/T', valn[0], '/', valn[1]

bw = 0.8
labx = []

plt.figure(figsize = (8,8))

print 'Plotted values:', valm

for i in range(3):
	b1x = 3*i
	b2x = 3*i+1

	plt.bar(b1x, valm[0][i], color='blue')
	plt.bar(b2x, valm[1][i], color = 'red')

	if i == 0:
		plt.legend(['Control', 'Target'], fontsize = 30, loc='best')
		#plt.legend(['CONTROL', 'TARGET'], fontsize = 30)

	sem1 = vals[0][1]/np.sqrt(valn[0][i])
	sem2 = vals[1][1]/np.sqrt(valn[1][i])
	plt.errorbar(b1x, valm[0][i], yerr = sem1, color='black', linewidth = 4)
	plt.errorbar(b2x, valm[1][i], yerr = sem2, color='black', linewidth = 4)

	# numbers of cells
	nfs = 10
	#plt.text(b1x + bw/5, valm[0][i] / 2, str(int(valn[0][i])), fontsize = nfs, color='white')
	#plt.text(b2x + bw/5, valm[1][i] / 2, str(int(valn[1][i])), fontsize = nfs)
	
	p_ks_sig = p_to_sig_str(p_ks[i])
	p_mw_sig = p_to_sig_str(p_mw[i])
	# p-values text
	# plt.text((b1x+b2x)/2.0, max(valm[0][i] + sem1, valm[1][i] + sem2) * 1.01, 'ks %.3f\nmw %.3f' % (p_ks[i], p_mw[i]))
	#plt.text((b1x+b2x)/2.0, max(valm[0][i] + sem1, valm[1][i] + sem2) * 1.01, 'ks    %s\nmw  %s' % (p_ks_sig, p_mw_sig))
	plt.text((b1x+b2x)/2.0, max(valm[0][i] + sem1, valm[1][i] + sem2) * 1.01, '%s' % (p_mw_sig), fontsize = 30)
	
	plt.ylabel('Place field similarity, r', fontsize = 30)

	labx.append(b2x-0.5)

	log_and_print(ld, '%s: %.3f / %.3f' % (CATEG_LABS[i], p_ks[i], p_mw[i]))

set_yticks_font(20)

maxy = 0.8
# maxy = max(valm[0] + valm[1]) * 1.4
# plt.ylim([0, 1.0])

# get from EVs - may not correspond to the file content !
minr=os.environ['MINR']
maxr=os.environ['MAXR']
maxpfs=os.environ['MAXPFS']
rinh=os.environ['RINH']
rdinh=os.environ['RDINH']
pfssuf=os.environ['PFSSUF']
lsuf = 'PART' if 'PART' in pfssuf else ''

# write to file !
f = open('PFS_SUMMARY_GROUPS.txt', 'a')
if meas == 7:
	f.write('%25s %8s %8s %3s %3s %4s %5s %5s %d        ' % (pfssuf, s1name, s2name, minr, maxr, maxpfs, rinh, rdinh, meas))
else:
	f.write('   ')

# write corrected p-values
for i in range(4):
	p_ks_sig = p_to_sig_str(p_ks[i])
        p_mw_sig = p_to_sig_str(p_mw[i])
	f.write('%5s/%-5s' % (p_ks_sig, p_mw_sig))

if meas == 1:
	f.write('\n')

if s2 == 4 and meas == 1:
	f.write('\n')

# split title in 2 by middle space
spos = []
for p in re.finditer(' ', TIT):
	spos.append(p.start())
# find closest to center
spos = np.array(spos)
sposc = spos
spos = np.abs(spos - len(TIT)/2)
mpos = sposc[np.argmin(spos)]
TIT = TIT[:mpos+1] + '\n' + TIT[mpos+1:]

plt.ylim([0, 1.0])
plt.yticks([0, 0.4, 0.8], fontsize=25)
plt.subplots_adjust(left=0.13, right=0.955)

TIT = argv[2]
#plt.title(TIT, fontsize=25)
plt.title('%s VS.\n%s\n simulated place fields' % (s1name, s2name), fontsize=25)

strip_axes(plt.gca())

plt.xticks(labx, CATEG_LABS, fontsize = 28)
plt.savefig(fig_save_dir() + 'PFS_%s_%s_PFS_%s_RINH_%s_RDINH_%s_%s_M%d_%s-%s.png' % (minr, maxr, maxpfs, rinh, rdinh, lsuf, meas, s1name, s2name))

plt.show()
