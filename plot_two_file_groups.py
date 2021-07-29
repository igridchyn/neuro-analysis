#!/usr/bin/env python

# plot data from two groups of files (obtained by find through given 

from matplotlib import pyplot as plt
from sys import argv
import subprocess
import numpy as np
from math import sqrt
import os
from scipy.stats import ttest_ind

if len(argv) < 2:
	print '(1)<wildcard 1> (2)<wildcard 2>'

wc1 = argv[1]
wc2 = argv[2]

corlist = len(argv) > 3
if corlist:
	print 'WARNING: correlation list mode ON'

cmd = 'find . -name "' + wc1 + '"'
sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
fl1 =  sp.communicate()[0].split()

cmd = 'find . -name "' + wc2 + '"'
sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
fl2 =  sp.communicate()[0].split()

if len(fl1) != len(fl2):
	print 'Different sizes of file lists'

v1 = []
v2 = []

# bad days
bd = []

for i in range(len(fl1)):
	if '1124' in fl1[i] or '0226' in fl1[i]:
		bd.append(i)
		#print 'WARNING: 1124/0226 excluded'
		#continue		

	apath = os.path.dirname(fl1[i]) + '/../about.txt'
	for line in open(apath):
		ws = line.split(' ')
		if ws[0] == 'swap':
			print i, fl1[i], fl2[i], line
			swap = bool(int(ws[1]))
	if swap:
		if not corlist:
			v1.extend([float(a) for a in open(fl1[i])])
			v2.extend([float(a) for a in open(fl2[i])])
		else:
			v1.extend([[float(l.split(' ')[0]), float(l.split(' ')[1])] for l in open(fl1[i])])
			v2.extend([[float(l.split(' ')[0]), float(l.split(' ')[1])] for l in open(fl2[i])])
	else:
		if not corlist:
			v2.extend([float(a) for a in open(fl1[i])])
			v1.extend([float(a) for a in open(fl2[i])])
		else:
			v2.extend([[float(l.split(' ')[0]), float(l.split(' ')[1])] for l in open(fl1[i])])
			v1.extend([[float(l.split(' ')[0]), float(l.split(' ')[1])] for l in open(fl2[i])])
		
mn = min(min(v1), min(v2))
mx = max(max(v1), max(v2))

plt.figure()

# plt.scatter(v1, v2)
# plt.plot([0, 1], [0, 1])

#if corlist:
#	v1 = [np.corrcoef([v[0] for v in v1], [v[1] for v in v1])[0, 1]]
#	v2 = [np.corrcoef([v[0] for v in v2], [v[1] for v in v2])[0, 1]]

print 'WARNING: RATE'
v1 = [(v[0] - v[1]) * 2/ (v[0] + v[1]) for v in v1]
v2 = [(v[0] - v[1]) * 2/ (v[0] + v[1]) for v in v2]

#plt.scatter(range(len(v1)), [(v1[i] - v2[i]) / v2[i] for i in range(len(v1))])
#plt.scatter(bd, [0] * len(bd), color='r')

bw = 0.2
v1 = np.array(v1)
v2 = np.array(v2)
v1 = v1[~np.isnan(v1) & ~np.isinf(v1) & (v1 != 0)]
v2 = v2[~np.isnan(v2) & ~np.isinf(v2) & (v2 != 0)]

#v1 = np.log(v1)
#v2 = np.log(v2)
m1 = -np.mean(v1)
m2 = -np.mean(v2)

#plt.bar([0, 1], [m1, m2], width = bw)
plt.bar([0], [m1], width = bw)
plt.bar([0.5], [m2], width = bw, color = 'Red')
plt.legend(['Target', 'Control'], fontsize = 20, loc='best')
plt.errorbar([0 + bw/2, 0.5 + bw/2], [m1, m2], yerr = [np.std(v1) / sqrt(v1.shape[0]), np.std(v2) / sqrt(v2.shape[0])], color = 'black', linewidth = 5, linestyle='None')
plt.xlim(0-bw, 0.7 + bw)
plt.gca().get_xaxis().set_visible(False)
plt.plot([-0.5, 1.0], [0, 0], color = 'black', linewidth = 3)
#plt.text(0.3, 0.12, '***', fontsize = 30)
plt.show()

print v1
print v2

if True:
	#for d in reversed(bd):
	#	del v1[d]
	#	del v2[d]
	#	print 'WARNING: Exclude ', d 

	v1 = np.array(v1)
	v2 = np.array(v2)
	ind = ~np.isnan(v1) & ~np.isnan(v2) #& (v1 > 0) & (v2 > 0)
	print ind
	v1 = v1[ind]
	v2 = v2[ind]
print v1
print v2
print np.mean(v1), np.std(v1) / sqrt(len(v1))
print np.mean(v2), np.std(v2) / sqrt(len(v2))

print 'T-test p-value: ', ttest_ind(v1, v2)[1]
