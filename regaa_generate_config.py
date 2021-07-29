#!/usr/bin/env python
from sys import argv

if len(argv) < 5:
	print 'USAGE: gen_conf.py <config file name> <starting electrode> <end electrode> <n skip> [<skip list>]'
	exit(1)

fname = argv[1]

conf = open(fname, 'w')

el_start = int(argv[2])
el_end = int(argv[3])

ypos = 70
# between channels
dy = 25
# between tetrodes
dyt = 40

# read skipped
nskip = int(argv[4])
skip = [int(argv[i]) for i in range(5, 5 + nskip)]

nel = 4

total_electrodes = el_end - el_start - len(skip) + 1

conf.write("""regaa2.0
0
1820
1014
30
50
10
1
""")

conf.write(str(total_electrodes) + '\n')

col = 0

for i in range(el_start, el_end + 1):
	if i in skip:
		continue
	conf.write(str(i) + ' 0 ' + str(ypos) + ' 0.005 ' + str(col) + '\n')

	if not ((i+1) % nel):
		ypos += dyt
		col += 1
	else:
		ypos += dy

conf.write("""0
0
0
0
0
0""")
