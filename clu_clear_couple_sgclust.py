#!/usr/bin/env python

import numpy as np
import scipy
import os
from sys import argv
import matplotlib.pylab as plt
from scipy import linalg
from scipy import spatial
import subprocess
import shutil

#=================================================================================================================
def onclick(event):
	print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % (
		event.button, event.x, event.y, event.xdata, event.ydata)
	if event.button == 2:
		print 'delete %.2f percent of closest to cluster %d spikes from cluster %d...' % (event.xdata, clun1, clun2)
		# TODO: no round
		i = round(event.xdata)	
		print '	step = ', step
		print '	i= ', i
		print 'len(imsort)= ', len(imsort)
		res_cut = scipy.array([res2[j] for j in imsort[0:(i/100 * len(imsort))]])
		clean_cluster(res_cut)
		print 'done :' + str(len(res_cut)) + ' spikes move to cluster ' + str(clun1)
		exit(0)
#=================================================================================================================
def ref_frac(rescut, ref_ms_1, ref_ms_2):
	diff = scipy.array([rescut[i] - rescut[i-1] for i in range(1, len(rescut))])
	i2 = sum(diff < 20 * ref_ms_1)
	i10 = sum(diff < 20 * ref_ms_2)
	return i2 / float(i10) if i10 > 0 else 0, i2, i10
#=================================================================================================================
def isi_upd(isi, ref_ms_1, ref_ms_2, i1, i2):
	if isi < 20 * ref_ms_1:
		i1 += 1
	if isi < 20 * ref_ms_2:
		i2 += 1
	
	return (i1, i2)
#=================================================================================================================
def isi_upd_rem(isi, ref_ms_1, ref_ms_2, i1, i2):
	if isi < 20 * ref_ms_1:
		i1 -= 1
	if isi < 20 * ref_ms_2:
		i2 -= 1
	
	return (i1, i2)
#=================================================================================================================
#=================================================================================================================
def ref_frac_inc(rescut, rescutnew, ref_ms_1, ref_ms_2, i1, i2):
	# both res are sorted
	rescutm = [0] * (len(rescut) + len(rescutnew))
	m = 0

	# print rescut, rescutnew

	if len(rescutnew) == 0:
		frac = i1 / float(i2) if i2 > 0 else 0
		return rescut[:], i1, i2, 0, frac

	i = 1
	j = 0

	# find first between rescut[0] and rescut[1]
	while j < len(rescutnew) and rescutnew[j] < rescut[0]:	
		# 2 new ISIs:
		(i1, i2) = isi_upd(rescut[0] - rescutnew[j], ref_ms_1, ref_ms_2, i1, i2)
		rescutm[m] = rescutnew[j]
		m += 1
		j += 1

	rescutm[m] = rescut[0]
	m += 1

	while i < len(rescut) and j < len(rescutnew):
		while i < len(rescut) and rescut[i] < rescutnew[j]:
			rescutm[m] = rescut[i]
			m += 1
			i += 1

		if i == len(rescut):
			break

		# 2 new ISIs:
		(i1, i2) = isi_upd(rescutnew[j] - rescut[i-1], ref_ms_1, ref_ms_2, i1, i2)
		(i1, i2) = isi_upd(rescut[i] - rescutnew[j], ref_ms_1, ref_ms_2, i1, i2)

		rescutm[m] = rescutnew[j]
		m += 1

		j += 1

	# assigne the rest
	if i >= len(rescut):
		rescutm[m:] = rescutnew[j:]
	else:
		rescutm[m:] = rescut[i:]

	frac = i1 / float(i2) if i2 > 0 else 0
	return rescutm, i1, i2, frac
#=================================================================================================================
def ref_frac_inc_rem(rescut, rescutrem, ref_ms_1, ref_ms_2, i1, i2):
	# both res are sorted
	# print rescut, rescutrem

	rescutm = [0] * (len(rescut) - len(rescutrem))
	m = 0;

	if len(rescutrem) == 0:
		frac = i1 / float(i2) if i2 > 0 else 0
		return rescut, i1, i2, frac

	i = 0
	j = 0
	# find first not excluded
	while rescut[i] == rescutrem[j] and i+1 < len(rescut):
		(i1, i2) = isi_upd_rem(rescut[i+1] - rescut[i], ref_ms_1, ref_ms_2, i1, i2)	
		i += 1
		j += 1
	
	while i < len(rescut) and j < len(rescutrem):
		while i < len(rescut) and rescut[i] < rescutrem[j]:
			# if m == len(rescutm):
			# 	print m, len(rescutm), i, rescut[i]
			rescutm[m] = rescut[i]
			m += 1
			i += 1

		if i == len(rescut):
			break

		# 2 new ISIs, now rescut[i] == rescutrem[j]
		# if previous has not been removed (and isi already discarded)
		if j == 0 or rescutrem[j-1] != rescut[i-1]:
			(i1, i2) = isi_upd_rem(rescut[i] - rescut[i-1], ref_ms_1, ref_ms_2, i1, i2)
		# TODO: update for case when >1 in a row have been removed (keep last non-removed and check if next has not been removed)
		if i+1 < len(rescut):
			(i1, i2) = isi_upd_rem(rescut[i+1] - rescut[i], ref_ms_1, ref_ms_2, i1, i2)

			# find previous not-removed and udpate if next is not removed
			k = i - 1
			l = j - 1
			while k >=0 and l >= 0 and rescut[k] == rescutrem[l]:
				k -= 1
				l -= 1
			if k >= 0 and (j + 1 == len(rescutrem) or rescutrem[j+1] != rescut[i+1]):
				(i1, i2) = isi_upd(rescut[i+1] - rescut[k], ref_ms_1, ref_ms_2, i1, i2)

		j += 1
		i += 1

	# print m,len(rescutm), i, len(rescut)
	# append the rest of the res
	rescutm[m:] = rescut[i:]

	frac = i1 / float(i2) if i2 > 0 else 0
	return rescutm, i1, i2, frac
#=================================================================================================================
#=================================================================================================================
def clean_cluster(res_cut1):
	fclu = open(path + '.clu.' + tetr)
	fclunew = open(path + '.clu.' + tetr + '.tmp', 'w')
	fclunew.write(str(nclu + 1) + '\n')
	fclu.readline()

	# print res_cut1

	i = 0
	for line in fclu.readlines():
		c = int(line[:-1])
		# print c, res[i]
		if c == clun2 and res[i] in res_cut1:
			fclunew.write(str(nclu + 1) + '\n')
		else:
			fclunew.write(line)
		i += 1
	
	fclu.close()
	fclunew.close()

	shutil.move(path+ '.clu.' + tetr + '.tmp', path + '.clu.' + tetr)
#=================================================================================================================

fig = plt.figure()
cid = fig.canvas.mpl_connect('button_press_event', onclick)

if len(argv) < 6:
	print 'Output cluster purity from number of spikes removed from the overlap of the two clusters'
	print 'Arguments: (1)<base-path> (2)<tetrode> (3)<cluster 1 - to fit Gaussian to> (4)<cluster 2 - to clean> (5)<refractory window size in ms, single-sided> (6)<step in %>'
	exit()

path = argv[1]
tetr = argv[2]
clun1 = int(argv[3])
clun2 = int(argv[4])
refr_ms_1 = int(argv[5])

f = open(path + '.fet.' + tetr)
dim = int(f.readline()[:-1])
x = scipy.fromfile(f, sep=' ')
x = x.reshape(x.shape[0] / dim, dim)
f.close()

fetdim = dim - 5
i = scipy.array(range(0, fetdim))
x = x[:, i]

fclu = open(path + '.clu.' + tetr)
nclu = int(fclu.readline()[:-1])
clu = fclu.read().split('\n')
clu = [int(c) for c in clu if len(c) > 0]
fclu.close()

fres = open(path + '.res.' + tetr)
res = fres.read().split('\n')
res = [int(r) for r in res if len(r) > 0]
fres.close()

# indices of cluster 1 elements
ind1 = scipy.array([i for i in range(0, len(clu)) if clu[i] == clun1])
fet1 = x[ind1, :]
res1 = [res[i] for i in ind1.tolist()]

# indices of cluster 2 elements
ind2 = scipy.array([i for i in range(0, len(clu)) if clu[i] == clun2])
fet2 = x[ind2, :]
res2 = [res[i] for i in ind2.tolist()]

# mean and inverted covariance of first cluster
stepf = fet1.shape[0] / 10000
# fet1 = fet1[range(0, fet1.shape[0], stepf),:]
# print step
cov1 = np.cov(scipy.transpose(fet1))
covi1 = linalg.inv(cov1)
m1 = scipy.mean(fet1, 0)

# distance from 2nd to 1st
mdists = [scipy.spatial.distance.mahalanobis(fet2[i,0:fetdim], m1,covi1) for i in range(0, fet2.shape[0])]

# sort
imsort = np.argsort(mdists)

# number of elements in cluster 2
n2 = ind2.shape[0]

# number of steps to cut part of cluster, 0.25% step
step = n2 / (int(argv[6]) if len(argv) > 6 else 400)

# iterate and count how many spikes are still in the refractory

ref_fracs = []
ref_fracs2 = []
calc_limit = 400 if len(argv) < 7 else int(argv[6])

# initial fractions and ISI counts
f1, i1_1, i2_1 = ref_frac(res1, refr_ms_1, 10)
f2, i1_2, i2_2 = ref_frac(res2, refr_ms_1, 10)
res_cut_2 = res2[:]
res_ext_1 = res1[:]

# to process with c++: write arrays
f = open('clu_clean.tmp', 'w')
f.write(str(len(res1)) + '\n')
for a in res1:
	f.write(str(a) + '\n');
f.write(str(len(res2)) + '\n')
for a in res2:
	f.write(str(a) + '\n');
for a in imsort:
	f.write(str(a) + '\n');

use_cpp = False


if use_cpp:
	command = 'clu_clear_couple clu_clean.tmp ' + str(refr_ms_1)
	process = subprocess.call(command.split());

	ffra = open('clu_clean.tmp.frac')
	ar = ffra.readline().split(' ')[:-1]
	for i in range(0, len(ar)/2):
		ref_fracs2.append(float(ar[2 * i]))
		ref_fracs.append(float(ar[2 * i + 1]))

	calc_limit = len(ref_fracs) + 1

print 'Start moving iterations...'
for i in range(1, 1 if use_cpp else calc_limit):
	#res_cut = scipy.array([res2[j] for j in imsort[(i * step):]])
	#res_cut = scipy.sort(res_cut)
	#ref_fracs.append(ref_frac(res_cut, refr_ms_1, 10))

	res_cut = scipy.array([res2[j] for j in imsort[((i - 1) * step):(i * step)]])
	res_cut = scipy.sort(res_cut)
	res_cut_2, i1_2, i2_2, frac2 = ref_frac_inc_rem(res_cut_2, res_cut, refr_ms_1, 10, i1_2, i2_2)
	ref_fracs.append(frac2)
	
	# add spikes from clu2 to clu1
	#res2_add = res1 + [res2[j] for j in imsort[0:(i*step)]]
	#res2_add = scipy.sort(res2_add)
	#ref_fracs2.append(ref_frac(res2_add, refr_ms_1, 10))

	res2_add = scipy.array([res2[j] for j in imsort[((i-1)*step):(i*step)]])
	res2_add = scipy.sort(res2_add)
	res_ext_1, i1_1, i2_1, frac1 = ref_frac_inc(res_ext_1, res2_add, refr_ms_1, 10, i1_1, i2_1)
	ref_fracs2.append(frac1)

plt.plot(scipy.array(range(1, calc_limit)) * 100.0/calc_limit, ref_fracs, label = 'Purity of the cluster being cleaned')
plt.plot(scipy.array(range(1, calc_limit)) * 100.0/calc_limit, ref_fracs2, 'g', label = 'Purity of receiver cluster')
plt.axhline(0.01, color='r')
plt.axhline(0.005, color='r')
plt.show()
