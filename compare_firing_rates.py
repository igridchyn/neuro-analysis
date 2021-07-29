#!/usr/bin/env python

from matplotlib import pyplot as plt
from sys import argv
from tracking_processing import whl_to_speed, whl_to_pos
from numpy import array, invert, corrcoef, mean, exp, log
import numpy as np
from iutils import *

def is_within_swr(res, swrf, win):
	swr = [int(s) for s in open(swrf) if len(s) > 0]
	
	isin = []
	resi = 0
	for s in swr:
		while res[resi] < s - win:
			isin.append(False)
			resi += 1
		while res[resi] < s + win:
			isin.append(True)
			resi += 1
	while resi < len(res):
		isin.append(False)
		resi += 1

	return isin

def is_within_running(res, whlf, speed_thold):
	whl = whl_to_pos(open(whlf), 0)
	speed = whl_to_speed(whl)

	isin = []
	for r in res:
		isin.append(speed[r / 480] >= speed_thold)

	return isin

def firing_rates(base, frm, to, s_type, s_file):
	clu = [int(c) for c in open(base + 'clu') if len(c) > 0]
	res = [int(r) for r in open(base + 'res') if len(r) > 0]

	ncell = max(clu)

	res_s = 0
	resi = 0

	while res[resi] < frm:
		resi += 1
	res_s = resi

	if to == 0:
		res_e = len(res)
	else:
		while resi < len(res) and res[resi] < to:
			resi += 1

		res_e = resi

	if s_type == 'w':
		isin = is_within_running(res, s_file, 5)
	elif s_type == 's':
		isin = is_within_swr(res, s_file, 2400)
	else:
		print 'Session type can be either s(sleep) or w(waking)'
		exit(1)

	print 'isin / res sizes: %d / %d' % (len(isin), len(res))

	clu = array(clu)
	clu[invert(isin)] = -1
	#clu = list(clu)

	# 0 for env1, 1 for env2
    whl = whl_to_pos(open(whlf), 0)
    speed = whl_to_speed(whl)
	envmap = np.zeros((res_e-res_s,1))
	for ir in range(res_s, res_e):
		if whl[res[ir] // 480][0] > ENV_BORD:
			envmap[ir-res_s] = 1

	frs = [[0], [0]]
	for c in range(1, ncell + 1):
		frs[0].append(clu[res_s:res_e][~envmap].count(c))
		frs[1].append(clu[res_s:res_e][envmap].count(c))
	
	#secs = (res_e - res_s) / 24000.0
	#secs = sum(isin[res_s:res_e]) / 24000.0

	secs = 0
	for i in range(res_s, res_e - 1):
		if isin[i]:
			secs += res[i+1] - res[i]
	secs /= 24000.0
		
	print 'Total seconds: %.1f' % secs

	return [f/secs for f in frs]

if len(argv) < 12:
	print 'Usage: ' + argv[0] + '(1)<basename for clu/res> (2)<from> (3)<to> (4)<type (s/w)> (5)<whl or swr timestamps> (6-10)<same for 2nd set> (11)<env border> (12)<PFS dump>'
	print 'Compare firing rates in 2 sessions: either waking (running) or sleep (SWRs)'
	exit(0)

argv = resolve_vars(argv)

frs1 = firing_rates(argv[1], int(argv[2]), int(argv[3]), argv[4], argv[5])
frs2 = firing_rates(argv[6], int(argv[7]), int(argv[8]), argv[9], argv[10])

frs1 = array(frs1)
frs2 = array(frs2)
#print frs1, frs2
#frlograts = log(frs1[1:]) - log(frs2[1:])
# rate score
frlograts = (frs2[1:] - frs1[1:]) / (frs2[1:] + frs1[1:])

if len(argv) > 11:
	pfr1 = []
	pfr2 = []
	MINPFR = 0.5
	for line in open(argv[11]):
			ws = line.split(' ')
			pfr1.append(float(ws[3]))
			pfr2.append(float(ws[4]))
	sel = [(pfr2[i] - pfr1[i])/(pfr2[i] + pfr1[i]) if pfr1[i] > MINPFR and pfr2[i] > MINPFR else 0 for i in range(len(pfr2))]
	sel = np.array(sel)

	print 'Correlation with selectivity: %.4f' % np.corrcoef(sel, frlograts)[0, 1]

print 'Correlation of FRs: %.2f' % corrcoef(array(frs1), array(frs2))[0,1] 
print 'Average increase in rate: %.2f' % exp(mean(frlograts))

ramping = []
slowing = []
for i in range(0, len(frs1)-1):
	if frlograts[i] < -2:
		slowing.append(i+1)
	if frlograts[i] > 1:
		ramping.append(i+1)
print 'Cells slowing ' + str(slowing)
print 'Cells ramping ' + str(ramping)

plt.hist(frlograts[np.invert(np.logical_or(np.isnan(frlograts), np.isinf(frlograts)))], 20)
plt.show()

plt.scatter(frs1, frs2)
plt.xlabel('Firing rates in ' + argv[1])
plt.ylabel('Firing rates in ' + argv[4])
plt.axvline(0.5, color='r')
plt.plot([0, 20], [0, 10])
plt.plot([0, 10], [0, 20])
plt.grid()
plt.show()

