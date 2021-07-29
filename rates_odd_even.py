#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
#from call_log import *
from scipy import stats
from collections import Counter

# calculate rates in odd/even intervals

if len(argv) < 2:
	print('USAGE: (1)<file with ses/ids> (2)<interval (in samples)>')
	exit(0)

INT = int(argv[2])

# read day, see if loaded already
# if not - read dsen, find session
# load and read
ddic = {}
prdic = {}
irdic = {}
ids = open(argv[1]).readlines()
for line in ids:
    ws = line.split()
    day = ws[2]
    
    if day not in ddic:
        desen = open(day + '/' + day + '.desen').readlines()
        nses = np.argmax(['fi' in d for d in desen]) + 1

        BASE = '%s/%s_%d.' % (day, day, nses)

        res = np.loadtxt(BASE + '.res')
        clu = np.loadtxt(BASE + '.clu')
        if len(clu) > len(res):
            clu = clu[1:]

        nclu = max(clu)

        rates_odd = Counter(clu[res // INT < INT/2])
        for k, value in rates_odd.items():
            rates_odd[k] = value * 2 / (res[-1])

        rates_even = Counter(clu[res // INT >= INT/2])
        for k, value in rates_even.items():
            rates_even[k] = value * 2 / (res[-1])

        for k in list(rates_odd.keys()):
            if k not in rates_even:
                rates_even[k] = 0
        for k in list(rates_even.keys()):
            if k not in rates_odd:
                rates_odd[k] = 0
           
        rates = np.hstack((rates_odd.values(), rates_even.values()))
        
        ddic[day] = rates

    rates = ddic[day]
    
    # string-identifiers day + id for dics
    pyrl = day + ws[3]
    intl = day + ws[4]
    if pyrl not in prdic:
        prdic[pyrl] = rates[int(ws[3]), :]
    if intl not in irdic:
        irdic[intl] = rates[int(ws[4]), :]

np.writetxt('rates_odd_even_pyr', np.array(prdic.values()))
np.writetxt('rates_odd_even_int', np.array(irdic.values()))
