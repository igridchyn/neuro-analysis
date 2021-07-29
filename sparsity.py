#!/usr/bin/env python

import numpy as np
from sys import argv
import os

if len(argv) < 4:
    print('USAGE: (1)<base> (2)<session> (3)<output E1> (4 - OPTIONAL)<output E2>')
    exit(0)

base = argv[1]
session = argv[2]
output1 = argv[3]

if len(argv) > 4:
    SPLIT = True
    output2 = argv[4]
else:
    SPLIT = False

c = 1
occor = np.genfromtxt(base + 'occ_' + session + '_nosm.mat' )
occ = occor / np.nansum(occor)

fout1 = open(output1, 'w')
if SPLIT:
    fout2 = open(output2, 'w')

OT=0

pfpath = base + str(c) + '_' + session + '_nosm.mat'
while os.path.isfile(pfpath):
    pf = np.genfromtxt(pfpath)

    # pf[pf < 0.00000001] = np.nan

    pfsq = np.square(pf)
    
    prod = np.multiply(pf, occ)

    prod[occor < OT] = np.nan

    try:
        halfx = pf.shape[1] // 2 if SPLIT else pf.shape[1]
        imaxx = np.nanargmax(pf) % pf.shape[1]
#        print('argmax-x: %d' % imaxx)
                #if imaxx >= halfx:
                    #prod[:, :halfx] = np.nan
                #else:
                        #prod[:, halfx:] = np.nan
        prod1 = prod.copy()

        if SPLIT:
            prod1[:, halfx:] = np.nan
            prod2 = prod.copy()
            prod2[:, :halfx] = np.nan
    except:
        print('Nan only')


    # (sum PiRi) ^ 2 / sum (PiRi ^ 2)
    # spars = np.nansum(prod) ** 2 / np.nansum(np.square(prod))
    spars1 = np.nansum(prod1) ** 2 / np.nansum(np.multiply(pfsq, occ))
    if SPLIT:
        spars2 = np.nansum(prod2) ** 2 / np.nansum(np.multiply(pfsq, occ))
    else:
        spars2 = 0

    print(str(c), ' sparsities: ', spars1, spars2)

    c += 1
    pfpath = base + str(c) + '_' + session + '_nosm.mat'

    fout1.write(str(spars1) + '\n')
    if SPLIT:
        fout2.write(str(spars2) + '\n')
