#!/usr/bin/env python

from sys import argv
from math import sqrt

# arguments: basename, goalx, goaly, radius, suffix, mint, maxt

if len(argv) < 8:
	print 'Arguments: (1)<basename> (2)<goal x> (3)<goal y> (4)<radius> (5)<suffix for output clu/res> (6)<start time> (7)<end time>'
	exit(0)

bname = argv[1]
gx = float(argv[2])
gy = float(argv[3])
rad = float(argv[4])
fnsuf = argv[5]
mint = float(argv[6])
maxt = float(argv[7])

whl = []

fwhl = open(bname + '.whl')
for line in fwhl:
	ws = line.split(' ')

	if len(ws) < 2:
		continue
	whl.append([float(ws[0]), float(ws[1])])
fwhl.close()

clu = []
fclu = open(bname + '.clu')
clu = [int(c) for c in fclu if len(c) > 0]
nclu = clu[0]
clu = clu[1:]

res = []
fres = open(bname + '.res')
res = [int(r) for r in fres if len(r) > 0]

print 'Length of clu: ', len(clu)

foutc = open(bname + fnsuf + '.clu', 'w')
foutr = open(bname + fnsuf + '.res', 'w')
foutc.write(str(nclu) + '\n')

ecnt = 0
for i in range(0, len(res)):
	t = res[i]

	if t < mint:
		continue
	if t > maxt:
		break

	whli = t / 512
	pos = whl[whli]

	dist = sqrt((pos[0] - gx) ** 2 + (pos[1] - gy) ** 2)
	if dist < rad:
		foutc.write(str(clu[i]) + '\n')
		foutr.write(str(t) + '\n')
		ecnt += 1

foutr.close()
foutc.close()

print 'Written %d entries around goal' % ecnt


