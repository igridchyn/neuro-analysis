#!/usr/bin/env python

import numpy as np
from sys import argv
from collections import Counter

def write_corrmat(f, mat):
        for i in range(mat.shape[0]):
                for j in range(i):
                        f.write('%d %d %.4f\n' % (i, j, mat[i, j]))

# Input: Clu/res/swr + number of SWRs , output: cofiring matrices

if len(argv) < 5:
	print 'USAGE: (1)<basename> (2)<number of SWRs per correlation block> (3)<shift in written timestamps> (4)<out path name (outpu APPENDED)>'
	exit(0)

base = argv[1]
nswr = int(argv[2])
shift = int(argv[3])
outpath = argv[4]

clu = [int(c) for c in open(base + 'clu') if len(c) > 0]
nclu = clu[0]
clu = clu[1:]

res = [int(c) for c in open(base + 'res') if len(c) > 0]

swr = []
for line in open(base + 'sw'):
	ws = line.split(' ')
	if len(ws) < 3:
		continue
	swr.append([int(ws[0]), int(ws[1]), int(ws[2])])

iswr = 0
ilastres = 0

fcorrmat = open(outpath, 'a')

while iswr < len(swr):
	if iswr >= len(swr) - 1:
		break

	popvecs = []

	# for current batch of swrs: from iswr to iswr+nswr	
	for i in range(nswr):
		tswrstart = swr[iswr + i][0]
		tswrend = swr[iswr + i][2]

		# find start of current swr
		while res[ilastres] < tswrstart:
			ilastres += 1

		istart = ilastres

		# find end of curren swr
		while res[ilastres] < tswrend:
			ilastres += 1

		iend = ilastres

		# pop vec from start till end
		pvc = Counter(clu[istart:iend])
		
		popvec = [pvc[j] for j in range(1, nclu + 1)]

		popvecs.append(popvec)

		if (iswr + i) >= (len(swr) - 1):
			break

	# correlation matrix
	
	pvmat = np.transpose(np.array(popvecs))
	corrmat = np.corrcoef(pvmat)

	fcorrmat.write('%d %d\n' % (swr[iswr + 1][0] + shift, swr[iswr + i][2] + shift))
	write_corrmat(fcorrmat, corrmat)

	iswr += nswr

