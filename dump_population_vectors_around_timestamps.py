#!/usr/bin/env python

from iutils import *
import numpy as np
from sys import argv

def get_population_vectors_around_timestamps(swrs, res, clu, WIN, SN, SINGLE_VEC, cmap, overlap):
	ires = 0
	popvecs = []
	cused = sum(cmap > 0) + 1

	print 'Using %d cells' % cused
	print '%d events' % len(swrs)

	for swi in range(0, len(swrs)):
		swr = swrs[swi]

		while res[ires] < swr - WIN:
			ires += 1

		# if going to skip
		if res[ires] >= swr + WIN:
			if SINGLE_VEC:
				popvecs.append(np.zeros((cused, 1)))
			print 'SKIP - no windows around %d' % swr

		# TODO: non-full windows: skipp or fill until the end ?
		while res[ires] < swr + WIN:
			popvec = np.zeros((cused, 1))
			for i in range(ires, ires + SN):
				if cmap[clu[i]] >= 0:
					popvec[cmap[clu[i]]] += 1

			if NORM:
				popvec[:,0] -= means
				popvec[:,0] /= stds

			popvecs.append(popvec)

			if SINGLE_VEC:
				break	

			ires += SN - overlap

		
	return popvecs

#===================================================================================================================================

if len(argv) < 10:
	print 'Usage: ' + argv[0] + ' (1)<dir with all.clu/res> (2)<timestamps file> (3)<WIN around> (4)<spike number> (5)<path to norm file or - > (6)<0/1 - single vector per timestampp> (7)<path to cmap> (8)<output path> (9)<spike windows overlap>'
	print 'Dump population vectors around given timestamps +- WIN, or only one window if specified'
	exit(0)

swrs = read_int_array(argv[2])
res = read_int_list(argv[1] + 'all.res')
clu = read_int_list(argv[1] + 'all.clu')
WIN = int(argv[3])
SN = int(argv[4])
NORM = argv[5] != '-'
if NORM:
	print 'Read normalizers ...'
	norm = read_float_array(argv[5])
	means = norm[:, 0]
	stds = norm[:, 1]

SINGLE_VEC = bool(int(argv[6]))

cmap = read_int_array(argv[7])
OVERLAP = int(argv[9])

popvecs = get_population_vectors_around_timestamps(swrs, res, clu, WIN, SN, SINGLE_VEC, cmap, OVERLAP)
write_array(popvecs, argv[8])
