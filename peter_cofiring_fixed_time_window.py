#!/usr/bin/env python
import numpy as np
from sys import argv

def write_corrmat(f, mat):
        for i in range(mat.shape[0]):
                for j in range(i):
                        f.write('%d %d %.4f\n' % (i, j, mat[i, j]))

if len(argv) < 4:
	print 'USAGE: (1)<basename for clu/res files> (2)<population time window (ms)> (3)<correlation frame window (ms)>'
	exit(0)

base = argv[1]
tpop = int(argv[2]) * 20
twin = int(argv[3]) * 20


clu = [int(c) for c in open(base + 'clu') if len(c) > 0]
nclu = clu[0]
clu = clu[1:]
res = [int(c) for c in open(base + 'res') if len(c) > 0]

fout = open(base + 'fixtwcorrs', 'w')

ires = 0
pvec = [0] * nclu
pvecs = []
tframe = 0
while ires < len(res):
	print 'T = ', tframe

	t = tframe		
	# for current frame : tframe to tframe+twin
	while ires < len(res) and res[ires] < tframe + twin:
		# current population vector : from t to t+tpop
		while ires < len(res) and res[ires] < t + tpop:
			pvec[clu[ires] - 1] += 1
			ires += 1

		pvecs.append(pvec)
		pvec = [0] * nclu
			
		t += tpop

	pmat = np.transpose(np.array(pvecs))
	mcorr = np.corrcoef(pmat)
	pvecs = []

	fout.write('%d %d' % (tframe, tframe + twin))
	write_corrmat(fout, mcorr)

	tframe += twin
