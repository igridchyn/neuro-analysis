#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import * 
from matplotlib import pyplot as plt
#import statsmodels

# detect High Synchrony Events : begining / peak  end

NPAR = 4
if len(argv) < NPAR:
	print 'USAGE: (1)<base for clu/res> (2)<des file> (3)<HSE window size> [-p=percentile {0.5|1|2|5|10}] [-se=(SWE extension to compare to) {slsw|sw}] [-sn=(spike number threshold) <integer>] [-sno=(spike number for onse) <integer>] [-cd=(detection cooldown, ms) <integer>]'
	exit(0)

op = parse_optional_params(argv[NPAR:])
# calculate MUA distribution in windows of given size
# take 20% quantile as a threshold for detection
# define events - start / end / peak
# compare to SWR for different windows sizes, choose best

HSWIN = 20 * int(argv[3])
BASE = argv[1]
DESPATH = argv[2]
des = [s[:-1] for s in open(DESPATH)]
clu = read_int_list(BASE + 'clu')
NCLU = clu[0]
clu = clu[1:]
res = read_int_list(BASE + 'res')

print res[-1]
scounts = [0] * (res[-1] / HSWIN + 1)

# TODO: cell type - only count INs
for i in range(len(res)):
	if des[clu[i] - 2] == 'p1':
		scounts[res[i]/HSWIN] += 1

outpath = BASE + 'hse'
if os.path.isfile(outpath):
	print 'ERROR: Output file exists at', outpath
	exit(1)

# quantiles: 0.5 Hz, 1 Hz
q05 = int(res[-1] / HSWIN * 0.005) # 1%  of windows to be HSE
q1 = int(res[-1] / HSWIN * 0.01) # 1%  of windows to be HSE
q2 = int(res[-1] / HSWIN * 0.02) # 2%  of windows to be HSE
q5 = int(res[-1] / HSWIN * 0.05) # 5%  of windows to be HSE
q10 = int(res[-1] / HSWIN * 0.1)  # 10% of windows to be HSE

iq_thold = gdvf(op, 'p', 2)
#q_thold = [q1, q2, q5, q10][[1,2,5,10].index(iq_thold)]
q_thold = int(res[-1] / HSWIN * iq_thold / 100.0)

# no quantiles in 1.14
#print 'Percentiles 1 Hz, 0.5 Hz:', np.quantile(scounts, q1), np.quantile(scounts, q2)
scounts_sorted = sorted(scounts)
print 'Percentiles 0.5%/1%/2%/5%/10% windows HSE:', scounts_sorted[-q05], scounts_sorted[-q1], scounts_sorted[-q2], scounts_sorted[-q5], scounts_sorted[-q10]
N_HSE = scounts_sorted[-q_thold]

sn = gdvi(op, 'sn', 0)
if sn > 0:
	N_HSE = sn
print 'CHOSEN SPIKE # THREHOLD', N_HSE

# threshold for onset and end
N_HSE_SUB = N_HSE * 2 / 3
sno = gdvi(op, 'sno', 0)
if sno > 0:
	N_HSE_SUB = sno
	print 'OVERRIDE THE SPIKE NUMBER THRESHOLD FOR HSE ONSET:', N_HSE_SUB
else:
	print 'USING DEFAULT SPIKE NUMBER THRESHOLD FOR HSE ONSET:', N_HSE_SUB

#plt.hist(scounts, 400)
#plt.show()

# write events list - start, end, peak; with 1 ms interval

# detection time step
DT = 20
t = HSWIN # window end
spiket = []
resi = 0
HSE = False
HSE_start = 0
HSE_start_prev = 0
HSE_end = 0
HSE_max = 0
HSE_maxt = 0
hses = []

CD = 20 * gdvi(op, 'cd', 50)

fout = open(outpath, 'w')

while t < res[-1]:
	# next window - remove and add
	while len(spiket) > 0 and spiket[0] < t-HSWIN+DT:
		spiket.pop(0)

	while resi < len(res) and res[resi] < t+DT:
		if des[clu[resi]-2] == 'p1':
			spiket.append(res[resi])	
		resi += 1

	t += DT

	# detect + cooldown = 50 ms
	if not HSE and len(spiket) > N_HSE_SUB and t > HSE_start_prev + CD:
		HSE = True
		HSE_start = t-HSWIN
	if HSE and len(spiket) > HSE_max and len(spiket) > N_HSE:
		HSE_max = len(spiket)
		HSE_maxt = t
	if HSE and len(spiket) < N_HSE_SUB:
		HSE = False
		HSE_end = t

		# only count if peak was reached
		if HSE_max > 0:
			#print 'HSE', HSE_start, HSE_maxt, HSE_end
			fout.write('%d %d %d\n' % (HSE_start, HSE_maxt, HSE_end))
			hses.append([HSE_start, HSE_maxt, HSE_end])
			HSE_start_prev = HSE_start

		HSE_max = 0
		HSE_maxt = 0

# compare to sw - distribution of mins distances between peaks
swpath = BASE + gdv(op, 'se', 'sw')
if not os.path.isfile(swpath):
	print 'WARNING: no SWR file found under', swpath
else:
	sw = read_int_list(swpath)
	swp = [s[1] for s in sw]
	isw  = 1
	mindists = []
	for ihse in range(1, len(hses)):
		# find first before and first after (or equal)
		while isw < len(swp)-1 and swp[isw] < hses[ihse][1]:
			isw += 1

		dt_b = hses[ihse][1] - swp[isw-1]
		dt_a = swp[isw] - hses[ihse][1]
		
		mindists.append(min(dt_b, dt_a))

	dur_hse = 0
	for hse in hses:
		dur_hse += hse[2] - hse[0]
	dur_hse /= float(len(hses)) * 20
	dur_sw = 0
	for s in sw:
		dur_sw += s[2] - s[0]
	dur_sw /= float(len(sw)) * 20
	print 'Average durations of events (ms): HSE=%.2f SWR=%.2f' % (dur_hse, dur_sw)

	# calculate match
	print '# of HSE: %d (%.2f Hz), # of SW: %d (%.2f Hz)' % (len(hses), len(hses)/float(res[-1])*20000, len(sw), len(sw)/float(res[-1])*20000)
	mindists = np.array(mindists)
	m100 = np.sum(mindists < 100*20) / float(len(mindists))
	m50 = np.sum(mindists < 50*20) / float(len(mindists))
	m20 = np.sum(mindists < 20*20) / float(len(mindists))
	m10 = np.sum(mindists < 10*20) / float(len(mindists))
	print '%.2f within 100ms, %.2f within 50ms, %.2f within 20ms, %.2f within 10ms' % (m100, m50, m20, m10)

	plt.hist(mindists, 100)
	#ecdf = statsmodels.distributions.ECDF(data)
	#plt.plot(ecdf.x, ecdf.y)
	#plt.show()
