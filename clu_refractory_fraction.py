#!/usr/bin/env python3

from sys import argv
#from termcolor import colored
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

if len(argv) < 3:
	print('OUTPUT: <fraction of ISI < [arg4] ms within ISI < [arg3] ms> 	<firing rate>')
	print('COLOR CODEW: Yellow : >0.5%, Red : >1%')
	print('ARGUMENTS: <base_path> <tetrode_number> <normal ISI (ms), default = 10> <refractory ISI (ms), default = 2>')
	exit()

base = argv[1]
tetr = argv[2]

#clup = base + '.clu.' + tetr
#resp = base + '.res.' + tetr
clup = base + '.clu'
resp = base + '.res'

clu = open(clup).read().split('\n')
res = open(resp).read().split('\n')

clu = [int(c) for c in clu if len(c) > 0]
res = [int(r) for r in res if len(r) > 0]

clun = max(clu) + 1
#clun = int(clu[0]) + 1
print(clun, 'clusters')

isis2 = [0] * clun
isis10 = [0] * clun
total = [0] * clun

last = [0] * clun

SR = 24000
thold = 0.005
thold2 = 0.01


isi1 = 0.002 if len(argv) < 5 else float(argv[4]) / 1000
isi2 = 0.01 if len(argv) < 4 else float(argv[3]) / 1000

for i in range(0, len(clu)):
	c = clu[i]
	r = res[i]

	if r - last[c] < isi1 * SR:
		isis2[c] += 1

	if r - last[c] < isi2 * SR:
		isis10[c] += 1

	total[c] += 1
	last[c] = r

# skip cluster #1
i=2
while i < clun:
	fr = clu.count(i) * 24000 / float(res[-1])
	fr_str = '%.2f Hz' % fr

	if (isis2[i] > 0):
		fr =  isis2[i]/float(isis10[i])
		
		pers =  ('%.2f%%') % (fr*100)
		if fr > thold2:
			print(bcolors.FAIL + str(i) + ': ' +  pers + bcolors.ENDC, fr_str)
		else:
			if fr > thold:
				print(bcolors.WARNING + str(i) + ': ' + pers + bcolors.ENDC, fr_str)
			else:
				print(i, pers, fr_str)
	else:
		print(i, '0', fr_str)
	i += 1

# print total
