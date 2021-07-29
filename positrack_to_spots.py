#!/usr/bin/env python

# positrack: ~50Hz
# spots: 30Hz

from sys import argv

x = []
y = []
t = []

if len(argv) < 2:
	print 'USAGE: (1)<input positrack file>, (2)<output spots file>'
	exit(0)

fin = open(argv[1])
fin.readline()

for line in fin:
	ws = line.split(' ')
	xs = float(ws[4])
	ys = float(ws[5])
	ts = int(ws[1])

	t.append(ts)
	x.append(xs)
	y.append(ys)
fin.close()

fout = open(argv[2], 'w')

DLEN= len(x)
# interpolation distance limit
ILIM = 10

framen = -1
ipos = 0
while ipos < DLEN:
	framen += 1
	tpos = framen * 1000 / 30
	
	while ipos < DLEN and t[ipos] < tpos:
		ipos +=1

	if ipos == DLEN:
		break

	# exact match
	if t[ipos] == tpos:
		fout.write('%.3f %.3f\n' % (x[ipos], y[ipos]))
		continue

	# find first valid point before the frame time
	ibef = ipos - 1
	while ibef >= 0 and x[ibef] < 0 and ipos - ibef < ILIM:
		ibef -= 1
	# valid point is too far
	if ibef == 0 or ipos - ibef == ILIM:
		fout.write('-1 -1\n')
		continue

	# find diest valid point after the frame time
	iaft = ipos
	while iaft < DLEN and x[iaft] < 0 and iaft - ipos < ILIM:
		iaft += 1
	if iaft - ipos == ILIM or iaft == DLEN:
		fout.write('-1 -1\n')
		continue

	# interpolate position
	tdbef = t[ipos] - t[ibef]
	tdaft = t[iaft] - t[ipos]
	xsp = (x[ibef] * tdbef + x[iaft] * tdaft) / (tdbef + tdaft)
	ysp = (y[ibef] * tdbef + y[iaft] * tdaft) / (tdbef + tdaft)

	fout.write('%.3f %.3f\n' % (xsp, ysp))

fout.close()
