#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
from iutils import *
from collections import Counter
from call_log import *

if len(argv) < 10:
	print 'USAGE: (1)<pfs file path - with firing rates and light responses> (2)<intervals path - in full format (start, peak, end)> (3)<res/clu base> (4)<selectivity threshold> (5)<file with light responses or - if responses from PFS shoudl be used> (6)<z-scoring path> (7)<output file> (8)<windows size (ms)> (9)<post-delay>'
	exit(0)

argv = resolve_vars(argv)

# log_call(argv)

pfspath =  argv[1]
intpath =  argv[2]
rcbase  =  argv[3]
SELTHOLD = float(argv[4])
resppath = argv[5]
zpath = argv[6]
outpath = argv[7]
pwin = int(argv[8])
padel = int(argv[9])

if os.path.isfile(outpath):
	print 'ERROR: output file exists!'
	exit(5)

# load peak firing rates and light responses
pfrse1 = []
pfrse2 = []
meanr_e1 = []
meanr_e2 = []
resp = []

# load firing rates and responses from the PFS file
for line in open(pfspath):
	vals = [float(f) for f in line.split(' ')]
	pfrse1.append(vals[3])
	pfrse2.append(vals[4])
	if len(vals) > 8:
		meanr_e1.append(vals[8])
		meanr_e2.append(vals[9])
	resp.append(vals[-1])

# load responses from response file - OVERRIDE loaded from PFS
if resppath != '-':
	resp = []
	for line in open(resppath):
		if len(line) > 1:
			resp.append(float(line))	
 
# NAN + selectivity filtering indices
pfrse1 = np.array(pfrse1)
pfrse2 = np.array(pfrse2)
notnan = ~np.isnan(pfrse1) & ~np.isnan(pfrse2)
ind1 = (pfrse1 > SELTHOLD * pfrse2) & notnan | np.isnan(pfrse2)
ind2 = (pfrse2 > SELTHOLD * pfrse1) & notnan | np.isnan(pfrse1)

print 'Number of environment selective cells (E1/E2) : %d / %d' % (sum(ind1), sum(ind2))

# load intervals for light effect quantification
wins = []
# print 'WARINING: TIME WINDOWS SHIFTED'
for line in open(intpath):
	vals = [int(i) for i in line.split(' ')]
	wins.append(vals)

# load res/clu
res = []
clu = []
for line in open(rcbase + 'res'):
	res.append(int(line))
for line in open(rcbase + 'clu'):
	clu.append(int(line) - 1)
print 'Length of clu/res: %d / %d' % (len(clu), len(res))
NC = max(clu) + 1

# calculate mean firing rates of all cells - in windows before and after
# (count total spikes in windows before and after)
ires = 0
iwin = 0
# rate arrays - before and after
ratesa = [0] * NC
ratesb = [0] * NC

# lists of event-wise firing rates (optionally, Z-scored)
rateslista = [[] for i in range(NC)]
rateslistb = [[] for i in range(NC)]

# POST-ACCOUNTING DELAY
PADEL = 24 * padel
print 'WARNING: POST-COUNTING DELAY:', PADEL
# for every window - collect population vector of rates and accumulate sum for mean rates
while ires < len(res) and iwin < len(wins):
	# find first spikes in the before-window
	while ires < len(res) and res[ires] < wins[iwin][0]:
		ires += 1

	popvec = [0] * NC
	# calculate before-popvec
	while ires < len(res) and res[ires] < wins[iwin][1]:
		popvec[clu[ires]] += 1
		ires += 1

	# update average firing rates
	time = (wins[iwin][1] - wins[iwin][0]) / 24000.0
	for c in range(NC):
		ratesb[c] += popvec[c] / time
		rateslistb[c].append(popvec[c] / time)

	# introduce delay after the light before accounting spikes
	while ires  < len(res) and res[ires] < wins[iwin][1] + PADEL:
		ires += 1

	# calculate after-popvec
	popvec = [0] * NC
	while ires < len(res) and res[ires] < wins[iwin][2] + PADEL:
		popvec[clu[ires]] += 1
		ires += 1
	time = (wins[iwin][2] - wins[iwin][1]) / 24000.0
	for c in range(NC):
		ratesa[c] += popvec[c] / time
		rateslista[c].append(popvec[c] / time)

	iwin += 1

# DEBUG
#DI=10
#plt.hist(rateslista[DI], 50)
#plt.show()

# DEBUG
#for c in range(1,100,2):
#	plt.hist(rateslistb[c], bins=range(200))
#	plt.show()

ratesa = np.array(ratesa)
ratesb = np.array(ratesb)
ratesa /= len(wins)
ratesb /= len(wins)

EXCLUDE = True

# BOTH INTERVALS - TO EXCLUDE PROPERLY ...
# load intervals for light effect quantification
bwins = []
# print 'WARINING: TIME WINDOWS SHIFTED'

if EXCLUDE:
	print 'WARNING: using both.tiemstamps.full.100ms to exclude FR estimation - only AFTER LIGHT !'
	for line in open('both.timestamps.full.100ms'): # % pwin
		vals = [int(i) for i in line.split(' ')]
	# !!! don't exclude the before part !
		vals[0] = vals[1]
		bwins.append(vals)
else:
	print 'WARNING: NO EXCLUSION!'





# create clu with excluded wins ... (for proper z-scoring)
iwin = 0 # next window to consider
ires = 0
cluexcl = []
while iwin < len(bwins) and ires < len(res):
	# add until the window starts
	while ires < len(res) and res[ires] < bwins[iwin][1]:
		cluexcl.append(clu[ires])
		ires += 1
		
	# skip
	while ires < len(res) and res[ires] < bwins[iwin][2]:
		ires += 1

	iwin += 1
# add till end of res:
while ires < len(res):
	cluexcl.append(clu[ires])
	ires += 1
# length of all itnervals - to account in rate calculatino:
totilen = sum([w[2]-w[1] for w in bwins])



# normalized by mean sleep-wise firing rates
print 'Window for z-scoring = %d ms' % pwin
ri = 0
dt = 24 * pwin
#cluc = Counter(clu)
cluc = Counter(cluexcl)



iwin = 0
# load mean and std rates from given file
if zpath != '-':
	ratesstds = []
	meanrates = []
	for line in open(zpath):
		[m, s] = [float(f) for f in line.split(' ')]
		meanrates.append(m)
		ratesstds.append(s)
else:
	# DEPRECATED
	# calculate starndard deviation in the given window
	meanrates = np.array([cluc[c] if c in cluc else 1 for c in range(NC)]) / float(res[-1] - totilen) * 24000.0# was dt
	t = 0
	pv = [0] * NC
	pvs = []
	while ri < len(res):
		while ri < len(res) and res[ri] < t + dt:
			pv[clu[ri]] += 1
			ri += 1
		t += dt

		if ri < len(res) and iwin < len(bwins) and res[ri] > bwins[iwin][1]:
			while ri < len(res) and res[ri] < bwins[iwin][2]:
				ri += 1
			iwin += 1

			# now advance t till res[ir]
			if ri < len(res):
				t = res[ri]
		else:
			pvs.append(np.array(pv) * 24000.0 / dt)

		pv = [0] * NC

	pvs = np.array(pvs)
	ratesstds = [np.std(pvs[:,c]) for c in range(NC)]


# DEBUG
print 'Mean rates:', meanrates
print 'Rate stds:', ratesstds
DIR=5
print 'Debug cells (%d-%d) mean rate: ' %(DI, DI+DIR), meanrates[DI:DI+DIR]




ratesstds = np.array(ratesstds)
meanrates = np.array(meanrates)

# correlation matrices before and after
#print 'WARNING: rates Z-scored before corr mat calculation'
#print 'WARNING: rates NORMALIZED, not Z-scored'
#for c in range(NC):
#	rateslista[c] = [(r-meanrates[c])/ratesstds[c] if ratesstds[c] > 0 else np.nan for r in rateslista[c]]
#for c in range(NC):
#	rateslistb[c] = [(r-meanrates[c])/ratesstds[c] if ratesstds[c] > 0 else np.nan for r in rateslistb[c]]
#for c in range(NC):
#	rateslista[c] = [(r/meanrates[c]) if meanrates[c] > 0 else 0 for r in rateslista[c]]
#for c in range(NC):
#	rateslistb[c] = [(r/meanrates[c]) if meanrates[c] > 0 else 0 for r in rateslistb[c]]
arateslista = np.array(rateslista)
arateslistb = np.array(rateslistb)
corrsa = np.corrcoef(arateslista)
corrsb = np.corrcoef(arateslistb)
np.save(outpath + '.corrmats', [corrsb, corrsa])

# calculate and write population vector correlations
pcorr1 = 0
pcorr2 = 0
print arateslistb.shape
for t in range(len(rateslistb)):
	pcorr1 += np.corrcoef(arateslistb[ind1,t], arateslista[ind1,t])[0,1]
	pcorr2 += np.corrcoef(arateslistb[ind2,t], arateslista[ind2,t])[0,1]
pcorr1 /= len(rateslistb)
pcorr2 /= len(rateslistb)
fpcorr = open(outpath + '.pcorr', 'w')
fpcorr.write('%f %f %d\n' % (pcorr1, pcorr2, len(rateslistb)))

# print meanrates
#ratesa /= meanrates
#ratesb /= meanrates
#print 'WARNING: NO Z SCORING PERFORMED, JUST NORM !'
ratesa -= meanrates
ratesb -= meanrates
ratesa /= ratesstds
ratesb /= ratesstds

# DEBUG
print 'Debug cell (%d-%d) z-scored before rates: ' % (DI, DI+DIR), ratesb[DI:DI+DIR]

meanb1 = np.nanmean(ratesb[ind1])
meana1 = np.nanmean(ratesa[ind1])
meanb2 = np.nanmean(ratesb[ind2])
meana2 = np.nanmean(ratesa[ind2])

rcorrs = np.array([np.corrcoef(rateslistb[c], rateslista[c])[0,1] for c in range(NC)])
print 'Mean correlation of rates before and after env1 / env2: %.2f / %.2f' % (np.nanmean(rcorrs[ind1]), np.nanmean(rcorrs[ind2]))
print 'Correlation of mean rates beforea and after env1 / env2: %.2f / %.2f' % (np.corrcoef(ratesa[ind1], ratesb[ind1])[0,1], np.corrcoef(ratesa[ind2], ratesb[ind2])[0,1])

# write all the output with all filtrable columns:
# PFR1 PFR2 RESPONSE RATESB RATESA
fout = open(outpath, 'w')

if len(meanr_e1) == 0:
	#print 'ERROR: no mean rates, terminate'
	print 'WARNING: no mean rates, write 0s'
	#exit(345)
	meanr_e1 = [0] * len(pfrse1)
	meanr_e2 = [0] * len(pfrse2)
	# print 'WARINIG: '

for c in range(NC):
	fout.write('%f %f %f %f %f %f %f %f %f\n' %(pfrse1[c], pfrse2[c], resp[c], ratesb[c], ratesa[c], meanrates[c], rcorrs[c], meanr_e1[c], meanr_e2[c]))
fout.close()

# ============================================[   PLOT   ]==================================================

# posopt
# PLOT = True
PLOT = False

if PLOT:
	plt.figure()
	plt.scatter(ratesb[ind1], ratesa[ind1])
	plt.scatter(ratesb[ind2], ratesa[ind2], color = 'r')
	plt.axhline(y=meana1)
	plt.axhline(y=meana2, color = 'r')
	plt.axvline(x=meanb1)
	plt.axvline(x=meanb2, color = 'r')
	plt.xlabel('Firing rate BEFORE')
	plt.ylabel('Firing rate AFTER')
	plt.show()
