#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < 4:
	print 'USAGE: (1)<mean> (2)<std> (3)<n> (4)<mean2> (5)<std2> (6)<n2>'
	exit(0)

m1 = float(argv[1])
s1 = float(argv[2])
n1 = int(argv[3])

m2 = float(argv[4])
s2 = float(argv[5])
n2 = int(argv[6])

#a = np.random.normal(m1, s1, n1)
#b = np.random.normal(m2, s2, n2)
a = []
b = []

nrep = 100
nsig = 0

for j in range(nrep):

    i = 0
    while i < n1:
        c = np.random.normal(m1, s1)
        if c > -0.6 and c < 1.0:
            a.append(c)
            i += 1

    i = 0
    while i < n2:
        c = np.random.normal(m2, s2)
        if c > -0.6 and c < 1.0:
            b.append(c)
            i += 1

    sw = stats.mannwhitneyu(a, b)
    #sw = stats.wilcoxon(a, b)

    if sw[1] < 0.05 : nsig += 1

print 'nsig', nsig
print 'binomial test', stats.binom_test(nsig, nrep, 0.5, alternative = 'greater')
