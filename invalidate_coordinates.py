#!/usr/bin/env python
from sys import argv

# invalidate all coordinates with x and y in the given range

dx = 20.15
dy = 22.63

f = open(argv[1])
fo = open(argv[1] + '.inv', 'w')
for line in f:
	whl = line[:-1].split(' ')
	x = float(whl[0])
	y = float(whl[1])

	invalidated = False
	if ((x > 119) and (x < (120 + dx))) or ((y > 0) and (y < dy)):
		invalidated = True

	# same check for big coords
	x = float(whl[2])
	y = float(whl[3])

	if ((x > 119) and (x < (120 + dx))) or ((y > 0) and (y < dy)):
		invalidated = True

	if invalidated:
		fo.write('1023 1023 1023 1023 ' + whl[4] + ' ' + whl[5] + '\n')
	else:
		fo.write(line)

f.close()
fo.close()
