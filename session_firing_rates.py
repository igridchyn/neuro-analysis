#!/usr/bin/env python2

from sys import argv
from iutils import *

if len(argv) < 2:
	print '(1)<clu file>'
	print 'CALUCLATE MEAN FIRING RATE OVER A SESSION'
	exit(0)

argv = resolve_vars(argv)

respath = argv[1].replace('clu', 'res')
fres = open(respath)
for line in fres:
	pass
sdur = int(line)

nspikes = [0] * 500
maxclust = 0

for line in open(argv[1]):
	c = int(line)
	if c > maxclust:
		maxclust = c

	nspikes[c] += 1

frs = []
fout = open(argv[1] + '.frs', 'w')
for c in range(maxclust + 1):
	frs.append(nspikes[c] * 24000 / float(sdur))
	fout.write(str(frs[-1]) + '\n')

print frs
