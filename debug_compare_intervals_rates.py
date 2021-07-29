#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *

# between int[0] and int[1]
def count_spikes(ints):
	nsp = [0] * NC
	ii = 0
	ires = 0
	while ires < len(res) and ii < len(ints):
		# reach interval start
		while ires < len(res) and res[ires] < ints[ii][0]:
			ires += 1

		# count spikes withing interval:
		while ires < len(res) and res[ires] < ints[ii][1]:
			nsp[clu[ires]] += 1
			ires += 1

		ii += 1
	return nsp

def totlen(ints):
	return np.sum([i[1]-i[0] for i in ints])

if len(argv) < 5:
	print 'USAGE: (1)<clu/res base> (2)<intervals 1> (3)<intervals 2> (4)<output file - for ratios>'
	exit(0)

argv = resolve_vars(argv)

base = argv[1]
clu = read_int_list(base + 'clu')
clu = [c+1 for c in clu]
res = read_int_list(base + 'res')
NC = max(clu) + 1

ints1 = read_int_array(argv[2])
ints2 = read_int_array(argv[3])

print ints1

# calculate mean rates of each cell in each of the intervals
nsp1 = count_spikes(ints1)
nsp2 = count_spikes(ints2)

nsp1 /= totlen(ints1) / 24000.0
nsp2 /= totlen(ints2) / 24000.0

rat = nsp1 / nsp2
rat[np.isnan(rat)] = 0
rat[np.isinf(rat)] = 0

#plt.hist(rat)
#plt.show()

fo = open(argv[4], 'w')
for r in rat:
	if r > 0:
		fo.write('%f\n' % np.log(r))
fo.close()

print 'Ratio of means:', np.nanmean(nsp1) / np.nanmean(nsp2)
