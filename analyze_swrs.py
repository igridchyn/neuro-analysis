#!/usr/bin/env python
from sys import argv
# imshow
import pylab as P
from matplotlib import pyplot as plt
import numpy as np
import scipy.cluster.hierarchy as sch
from numpy import log
from tracking_processing import whl_to_pos, whl_to_speed
from imath import gaussian
from call_log import *
from iutils import *
# ===================================================================================================================================================================================================
def generate_pop_vector_distances(pops):
	l = pops.shape[0]
	dists = np.zeros((l, l))
	for i in range(0, l):
		for j in range(0, i+1):
			# Frobenius
			dists[i, j] = np.linalg.norm(pops[i,:] - pops[j,:])
			# assembly-based
			#diff = pops[i,:] - pops[j,:]
			#dists[i, j] = (sum(diff[:13]) - sum(diff[13:]))**2
			dists[j, i] = dists[i, j]
	return dists
# ===================================================================================================================================================================================================
def pop_vec(swr):
	# swr x pop. vector
	swrpop = np.zeros((len(swr), coin))
	# TODO: cache beginnings
	i = 0
	si = 0
	# print 'WARNING: only part of SWRs is used for calculating the statistics'
	for s in swr:
		# find beginning of the swr
		#while i < len(res) and res[i] < s - det_delay: # TIME
		while i < len(res) and res[i] < s:
			i += 1
		# sharp-wave spike number in each cluster
		popv = np.zeros((coin, 1))
		#while i < len(res) and res[i] < s + dur: # TIME
		for j in range(i-nspikes/2, i+nspikes/2): 
			popv[clu[j]] += 1 # i TIME
			# i += 1 # TIME

		for j in range(0, coin):
			sn[j][popv[j, 0]] += 1
		
		swrpop[si][:] = popv[:,0]	
		si += 1

	return swrpop
# ===================================================================================================================================================================================================
if len(argv) < 7:
	print 'Usage: ' + argv[0] + '(1)<file with swrs> (2)<directory with all.[clu|res]> [(3)<2nd swr file for comparison>] (4)<fixed dumber of spikes> (5)<swap> (6)<day>]'
	print 'Compare firint rates of two groups of cells in the two sets of events'
	exit(0)

argv = resolve_vars(argv)

swap = bool(int(argv[5]))

ld = log_call(argv)

fswrs = open(argv[1])
fbase = argv[2]

swr = []
for line in fswrs:
	swr.append(int(line[:-1]))
print len(swr), ' SWRs loaded'
fswrs.close()

nspikes = int(argv[4])

daycells = {

# COI - clusters of interest
'1217' : [[13,14,22,23,36,39,61,68,70,116,117,120,121], [4,33,43,58,65,66,69,71,79,92,94,111]],
'1220' : [[23, 28, 29, 33, 35, 49, 66, 70, 71, 73, 75, 80, 82],
[16, 31, 42, 46, 48, 78, 85]],
# 1221 - 14/15 (2nd / 1st) - FIRST CLUSTERING
#coi1 = [ 47, 30, 17, 42, 58, 61, 69, 75, 77, 90, 92] # 14-, 29-, 24-
#coi2= [ 8,10, 15, 11, 13, 35, 49, 65, 91] # 24-, 9-

# 1221 - 2nd clustering
#coi1 = [32,56,59,87,88,100,109,110,117,82]
#coi2 = [16, 26,27,46,57,71,86,125, 52,90] # was 16 before in the beginning; 86 has in both !!! 60-, 
'1221':[
[8, 9, 10, 11, 13, 15, 16, 35, 49, 57, 65, 87, 88, 91],
[17, 24, 25, 29, 30, 42, 43, 47, 58, 64, 66, 75, 90, 92, 94]],

# JC-164
#coi1 = [10, 14, 16, 25, 26, 33, 43, 44, 46, 47, 53, 56, 63] # -64
#coi2 = [11, 22, 29, 32, 34, 35, 41, 45, 52, 55, 71, 72] # -58, -4

# C / 0226 - 16l cells
#coi1 = [20, 21, 41, 46, 47, 48, 49, 57, 68, 74, 84, 89, 114, 146, 147, 164, 165, 167]
#coi2 = [11, 14, 16, 23, 25, 30, 32, 53, 59, 116, 117, 125, 127, 128, 138, 149, 157, 178]

# C / 0226 - 9l cells
'0226':[
# cell_selectivity.py ./ jc184_0226_9l.whl 2 200 4 0.5
[20, 32, 46, 48, 49, 57, 68, 74, 85, 96, 114, 115, 119, 132, 136, 141, 146, 164, 165, 175],
[8, 14, 16, 18, 25, 39, 43, 45, 59, 81, 110, 117, 131, 138, 142, 157, 169, 172, 178]],

# C / 0226 - 9l CELLS, 
# cell_selectivity.py ./ jc184_0226_9l.whl 4 200 4 0.5
# coi1 = [20, 48, 57, 68, 96, 114, 115, 119, 132, 136, 141, 146]
# coi2 = [14, 39, 110, 117, 131, 169, 178]

'1123':[ # - new 2 180 4 0.5 - BEST
[3, 4, 7, 8, 10, 20, 24, 26, 33, 35, 39, 40, 42, 47, 54, 55, 59, 73],
[22, 23, 46, 63, 67, 69, 74]],

'1124':[ # - !!! FACTOR OF 2 THRESHOLD !!!
[3, 4, 5, 9, 13, 14, 16, 17, 37, 49, 56, 79],
[11, 24, 25, 55, 57, 59, 61, 70]],

'1125':[ #- new 2 180 4 0,5
[2, 3, 4, 26, 31, 33, 34, 36, 37, 38, 44, 50, 64, 67, 68, 72, 75, 81, 108, 119],
[30, 42, 60, 73, 77, 78, 113]],

'1130':[# - new : 4 180 4 0.5
[3, 4, 12, 18, 19, 36, 37, 43, 45, 49, 59, 68, 86, 88],
[20, 39, 41, 42, 67, 72, 77, 85]],

'1201':[# - 4 200 4 0.5
[34, 50, 62, 65, 68, 75, 79, 91, 97],
[2, 10, 13, 16, 17, 18, 54, 55, 59, 60, 71, 82, 83, 88, 93]],

# B / 0106
#coi1 = [4, 22, 28, 49, 75, 82, 86]
#coi2 = [7, 9, 23, 24, 26, 31, 33, 42, 65, 73, 74, 79, 80, 89, 90, 92]

'0106':[# - new, ratio 2, speed 4, fr 0.5, sep 180
[4, 22, 28, 49, 75, 82, 86],
[7, 9, 23, 24, 26, 31, 33, 42, 65, 73, 74, 79, 80, 89, 90, 92]],

'0107':[
[22, 24, 25, 36, 48, 71, 82, 86, 90],
[3, 4, 6, 8, 13, 18, 19, 20, 31, 37, 50, 55, 56, 68, 84]],

'0109':[
[3, 15, 24, 28, 30, 31, 38, 39, 40, 41, 44, 54, 73],
[17, 18, 19, 42, 47, 53, 71]],

'0112':[# - 2 200 4 0.5
[3, 6, 11, 12, 13, 21, 24, 29, 32, 37, 62, 64, 65, 66, 73, 75, 84, 90],
[18, 47, 59, 63, 70, 71, 77, 80, 85]],

'0227':[
[8, 13, 15, 23, 31, 33, 72, 83, 91, 93, 94, 96, 105],
[7, 9, 10, 17, 26, 38, 56, 64, 73, 74, 77, 81, 103]],

'0301':[# FRAC=4, ST=8, FRTHOLD=5
[9, 21, 46, 47, 73, 80, 90, 96, 111, 119, 120, 123, 126, 127, 134, 147, 155, 156, 166],
[3, 58, 59, 63, 64, 68, 75, 76, 82, 83, 87, 91, 93, 107, 115, 116, 136, 149, 157, 172]],

'0304':[
[7, 15, 27, 30, 35, 49, 68, 70, 86],
[34, 39, 55, 73, 91]],

'0428':[
[2, 4, 12, 15, 19, 22, 24, 73, 74, 99, 113, 114, 115, 123, 126, 133, 145, 157, 162],
[8, 84, 89, 107, 110, 116, 138, 150, 156]],

'0429':[
[2, 5, 26, 32, 54, 72, 73, 89, 93, 99, 200, 205, 215, 216, 222, 231, 246, 248, 254, 257],
[25, 29, 33, 53, 62, 67, 86, 117, 122, 137, 182, 183, 185, 197, 202, 204, 219, 247]],

'0430':[
[5, 14, 47, 51, 64, 78, 79, 100, 120, 123, 124, 136, 140, 142, 152, 158, 163, 169, 184, 187],
[20, 21, 26, 30, 33, 53, 67, 75, 76, 103, 105, 107, 130, 137, 146, 147, 155, 156, 159, 174, 178, 180, 192]],

'0501':[
[3, 17, 23, 48, 50, 53, 55, 69, 73, 85, 91, 98, 99, 100, 129],
[7, 41, 56, 57, 83, 112, 133]]}

[coi1, coi2] =  daycells[argv[6]]

coi = coi1 + coi2
coin = len(coi)
# to have clu numbers from 0 to coin
cmap = [-1] * (max(coi) + 1)
for i in range(0, coin):
	cmap[coi[i]] = i
print 'cmap = ', cmap
# load clu and res
clu = []
res = []
fclu = open(fbase + 'clu')
fres = open(fbase + 'res')
while True:
	l = fclu.readline()
	if not l:
		break
	c = int(l[:-1])
	r = int(fres.readline()[:-1])
	if c in coi:
		clu.append(cmap[c])
		res.append(r)
fclu.close()
fres.close()
print len(clu), ' spikes read'

# duration, long - 50/60/30
dur = 1 * 24

st_after_swr = []
st_after_e1 = []
st_after_e2 = []

i = 0
# detection delay, long - 35/45/20
det_delay = 40 * 24
for s in swr:
	while i < len(res) and res[i] < s - det_delay:
		i += 1

	while i < len(res) and res[i] < s + dur:
		if clu[i] >=0 and clu[i] < len(coi1): # in coi2:
			st_after_e2.append(res[i] - (s - det_delay))
		if clu[i] >= len(coi1): # in coi1:
			st_after_e1.append(res[i] - (s - det_delay))
		st_after_swr.append(res[i] - (s - det_delay))
		i += 1

#print st_after_e2
#print st_after_e1
print sum(np.array(clu) == 1)
print 'Relative F.R.: %.2f' % (len(st_after_e2) / float(len(st_after_e1)))

# plt.hist(st_after_e2, 17, normed=0)
# plt.hist(st_after_e1, 17, normed=0, color='r')
# plt.show()

# spike number distribution
SMX = 200
# spike number
sn = np.zeros((len(coi), SMX))

swrpop = pop_vec(swr)

# if need to compare two sets of SWRs
if len(argv) > 3:
	swrpop2 = pop_vec([int(s) for s in open(argv[3]) if len(s) > 0])

# plot and dump numbers of spikes
bwid = 0.3
meann = np.mean(swrpop, axis=0)
stds = np.std(swrpop, axis=0)
print meann

#plt.bar(range(0, coin), meann,bwid) #, yerr=stds)
if len(argv) > 3:
	means2 = np.mean(swrpop2, axis=0)
	stds2 = np.std(swrpop2, axis=0)
#	plt.bar(np.array(range(0, coin)) + 0.3, np.mean(swrpop2, axis=0), bwid, color = 'r') #, yerr=stds2)
#
#plt.show()

print 'Meann:', meann

#meanrat = means2/meann
meanrat = [(means2[i] - meann[i]) * 2 / (means2[i] + meann[i]) for i in range(means2.shape[0])]
if swap:
	meanrat = [-m for m in meanrat]

# meanrat[meann == 0] = 0
#plt.bar(range(0,coin), meanrat)
# plot sorted
plt.bar(range(0, len(coi1)), np.sort(meanrat[0:len(coi1)]))
plt.bar(range(len(coi1), coin), np.sort(meanrat[len(coi1):]), color = 'r')
#plt.bar(range(0, len(coi1)), log(np.sort(meanrat[0:len(coi1)])))
#plt.bar(range(len(coi1), coin), log(np.sort(meanrat[len(coi1):])), color = 'r')

plt.xlabel('Cell ID')
#plt.ylabel('Log ratio of FRs in the two SWR groups : LOG(FR before NON-INH / FR before INH)')
plt.ylabel('Rate score ')
plt.legend(['Cells with place field in ENV 1 only', 'Cells with place field in EVN 2 only'], loc=0)
plt.title('Selective place cell firing in events confidently classified \nas one of the environments (top 10% in each class)')
plt.grid()

fout = open(argv[2] + 'sel2.e1', 'w')
for i in range(len(coi1)):
	fout.write('%f %f\n' % (means2[i], meann[i]))
	#fout.write('%f\n' % meanrat[i])
fout.close()
fout = open(argv[2] + 'sel2.e2', 'w')
for i in range(len(coi1), len(coi)):
	#fout.write('%f\n' % meanrat[i])
	fout.write('%f %f\n' % (means2[i], meann[i]))
fout.close()

#plt.set_xticklabels(coi)
plt.savefig(ld + 'SELECTIVITY.png')
plt.show()

print 'Mean ratio of firing rates change: %.2f' % (np.mean(meanrat[:len(coi1)]) / np.mean(meanrat[len(coi1):]))


print 'WARNING: EARLY EXIT BECAUSE OF DUMP RUN!'
exit(0)


# normalize firing rates
for c in range(0, coin):
	swrpop[:, c] = (swrpop[:, c] - np.mean(swrpop[:, c])) / np.std(swrpop[:, c])

# smooth IFRs
g = gaussian(11, 4)
print 'Gaussian shape: ', g.shape
print g
for c in range(0, coin):
	swrpop[:, c] = np.convolve(swrpop[:, c], g, mode='same')

# !!! FILTER FOR : speed (load whl), overall FR (just sum if it's already normalized)
# !!! DO K-MEANS

# !!!
print 'WARNING, only subset of population vectors is used for hierarchical clustering'
# swrpop = swrpop[swrpop.shape[1]/2:,:]

# visualize covariance matrix of spike counts
swrpopcorr = np.corrcoef(swrpop.transpose())
#swrpopcorr = generate_pop_vector_distances(swrpop)

print 'Done distances'

# reoder wrt cluster hierarchy
swrpopdist = swrpopcorr

plt.matshow(swrpopdist)
plt.show()

# COMPLETE
dosort = True
if dosort:
	# 1217 waking classification errors:
	# 	average : 2 errors, complete : 6 errors; centroid SHIT; median SHIT; single SHIT
	# 	
	Y = sch.linkage(swrpopdist, method='average') # single !complete average weighted centroid median ward
	Z = sch.dendrogram(Y, orientation='right')
	index = Z['leaves']
	swrpopdist = swrpopdist[index,:]
	swrpopdist = swrpopdist[:,index]

	print 'SWR-wise population vector Correlation matrix'
	print swrpopdist

	plt.matshow(swrpopdist)
	plt.show()

# for WAKING: calculate precision, may be more complicated
il = len(index)
index = np.array(index)
print 'Classification precision: %.2f' % ((sum(index[0:il/2] < il/2) + sum(index[il/2:] > il/2)) / float(il))


#for i in range(0, coin):
#	print 'Number of spikes in SWR distribution for cluster ', i, ': ', sn[i][0:5]
#	print 'Average and std for 1 and more spikes: ', np.mean(sn[i][1:]), ', ',  np.std(sn[i][1:])
	# plt.bar(range(1, SMX), sn[i][1:])
	# plt.show()


# check if swr similarity correlates with the distance between them
timediffs = []
similarities = []
REACH = 1
TIMELIMIT = 24000 * 1000

#print 'Shuffle correlations...'
#np.random.shuffle(swrpopcorr)

for si in range(0, len(swr)):
	for n in range(REACH, REACH + 1):
		if si + n >= len(swr):
			break
		if not np.isnan(swrpopcorr[si, si+n]) and swr[si+n]-swr[si] < TIMELIMIT:
			timediffs.append(swr[si + n] - swr[si])
			similarities.append(swrpopcorr[si, si+n])

plt.scatter(timediffs, similarities, s=1)

plat.savefig(ld + 'SIMILARITIES.png')

plt.show()

print 'Median and std of simialrity of neighbouring pairs: %f / %f' % (np.median(similarities), np.std(similarities))

print 'Number of SWR pairs: ', len(timediffs)
print 'Correlation of time difference between SWR and their population simlarity: ', np.corrcoef(timediffs, similarities)
