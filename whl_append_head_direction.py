#!/usr/bin/env python

from sys import argv

def fix_hd():
	R = 50
	hd1 = []
	hd1.extend(hd[0:R/2])
	for i in range(R/2, len(hd) - R/2):
		s = sum(hd[i-R/2 : i+R/2])
		if s > R*4/5 and hd[i] < 0:
			#print 'fix -1'
			hd1.append(1)
		elif s < -R*4/5 and hd[i] > 0:
			#print 'fix +1'
			hd1.append(-1)
		else:
			hd1.append(hd[i])

	hd1.extend(hd[len(hd)-R/2:])
	return hd1
# ================================================================================================

if len(argv) < 2:
	print 'Usage: (1)<whl file>'
	print 'Outoput: (1).hd - whl file with head direction appended'
	print 'WARNING: currently working only for the linearized data'
	exit(0)

whl = []
f = open(argv[1])
for line in f:
	if len(line) < 5:
		continue
	whl.append([float(w) for w in line.split(' ')])

# first
hd = []
last = 1
for w in whl:
	if w[0] < 1000:
		hdi = 1 if w[1] > w[3] else -1
		hd.append(hdi)
		last = hdi
	else:
		hd.append(last)

# fix jumps of 0-2 if 80% around (50) is another direction
#for i in range(10):
#	hd = fix_hd()

current = hd[0]
n = 0
i = 1
lens = []
while i < len(hd):
	if hd[i] != current:
		current = hd[i]
		lens.append(n)
		n = 0
	else:
		n += 1
	
	i += 1
	
print lens	

MX = 400
YALL = 1
for i in range(len(whl)):
	if hd[i] == 1:
		if whl[i][0] < 1000:
			whl[i][0] += MX
			#whl[i][1] = YALL
		if whl[i][2] < 1000:
			whl[i][2] += MX
			#whl[i][3] = YALL
	else:
		if whl[i][0] < 1000:
			#whl[i][1] = YALL
			whl[i][0] += 10
		if whl[i][2] < 1000:
			#whl[i][3] = YALL
			whl[i][2] += 10

fo = open(argv[1] + '.hd', 'w')
for wh in whl:
	fo.write('%f %f %f %f %d %d\n' % (wh[0], wh[1], wh[2], wh[3], int(wh[4]), int(wh[5])))
fo.close()

# print hdi
