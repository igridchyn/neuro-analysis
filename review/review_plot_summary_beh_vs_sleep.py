#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'


if len(argv) < 2:
	print 'USAGE: (1)<file with correlations and confidence intervals>'
	exit(0)

bsstats = np.loadtxt(argv[1])

bscors = bsstats[:,0].reshape((3,5))
tmp = bscors

bslow = bsstats[:,1].reshape((3,5))
bshigh = bsstats[:,2].reshape((3,5))
ps = bsstats[:,3].reshape((3,5))

bscors[1,:] = -bscors[1,:]
#bscors = bsstats[:,0].reshape((5,3)).transpose()

S = 4
bscors_ext = np.zeros((3, S * 5))
for c in range(5):
    for i in range(S):
        bscors_ext[:,S*c + i] = bscors[:,c]

meancor = np.mean(bscors)

print 'p-values:', ps

plt.figure(figsize=(19,5))

# put text
for r in range(3):
    # calculate new intervals based on the corrected p-values!
    psar = ps[r,:]
    corpsar = np.argsort(psar)
    pmult = [0] * 5

    mults = [0] * 5
    for i in range(5):
        mults[corpsar[i]] = (0.05 / (5 - i))
        #pmult[corpsar[i]] = 5-i
        ps[r,i] *= 5-i
        ps[r,i] = min(ps[r,i], 1.0)

    print 'ps corrected', psar

    for c in range(5):
        bound = - stats.norm.ppf(mults[c] / 2)
        cci = corr_conf_interval(bscors[r,c], 21, bound)
        print cci

        #plt.text(c*S-0.1, r+0.1, '%.2f (%.2f,%.2f)' % (bscors[r,c], bscors[r,c]-bslow[r,c],bscors[r,c]+bshigh[r,c]), color='white' if bscors[r,c] < meancor else 'black', fontsize=22)
        plt.text(c*S-0.2, r+0.1, '%.2f (%.2f,%.2f), %.2f' % (bscors[r,c], bscors[r,c]-cci[0],bscors[r,c]+cci[1], ps[r,c]), color='white' if bscors[r,c] < meancor else 'black', fontsize=22)

TFS = 20
plt.yticks([0,1,2], ['Number of\ncrossings', 'First trial\npath length', 'Dwell time'], fontsize=TFS)
plt.xticks(np.arange(S/2-0.5, 5*S+S/2, S), ['Non-theta sleep %', 'Mean delta power', 'Number of HSE', 'Number of\ndisrupted HSE', 'Mean SWR rate'], fontsize=TFS)

plt.imshow(bscors_ext, vmin=-0.31, vmax=0.52)
plt.colorbar(orientation = 'horizontal')
plt.subplots_adjust(left=0.08, right=0.995)

plt.show()
