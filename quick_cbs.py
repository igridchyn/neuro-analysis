#!/usr/bin/env python

from matplotlib import pyplot as plt
from sys import argv
from tracking_processing import *
from iutils import *
from call_log import *

if len(argv) < 9:
	print'(1)<base dir> (2)<base name : jc181_1130_ > (3)<learning session> (4)<post-probe session> (5)<post-learning session> (6)<distribution file / "-"> (7)<bin size (tracking)> (8)<speed threshold>'
	print 'QUICK CB tracking analyses'
	exit(0)

logdir = log_call(argv)

basedir = argv[1]
basename = argv[2]
sl = argv[3]
spostp = argv[4]
spostl = argv[5]
fdist = argv[6]
bsize = int(argv[7])
speed_thold = float(argv[8])

whll = whl_to_pos(open(basedir + '/' + sl + '/' +  basename + sl + '.whl.original'), False)
whlpp = whl_to_pos(open(basedir + '/' + spostp + '/' +  basename + spostp + '.whl'), False)
whlpl = whl_to_pos(open(basedir + '/' + spostl + '/' +  basename + spostl + '.whl'), False)

# maps, assume x y > 0
ml = occupancy_map(whll, bsize, speed_thold)
mpostl = occupancy_map(whlpl, bsize, speed_thold)
mpostp = occupancy_map(whlpp, bsize, speed_thold)

# sharey/x = True
psize = 1
f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2,3)
ax1.imshow(ml, interpolation = 'none', origin='lower')
ax1.set_title('Learning')
ax2.imshow(mpostp, interpolation = 'none', origin='lower')
ax2.set_title('Post-probe')
ax3.imshow(mpostl, interpolation = 'none', origin='lower')
ax3.set_title('Post-learning')
cthold = 0.5
# print whll[0:1000]
whll = [w for w in whll if w[0] > 0 and w[1] > 0]
whlpp = [w for w in whlpp if w[0] > 0 and w[1] > 0]
whlpl = [w for w in whlpl if w[0] > 0 and w[1] > 0]
ax4.scatter([w[0] for w in whll ], [w[1] for w in whll ], s=psize)
ax5.scatter([w[0] for w in whlpp ], [w[1] for w in whlpp ], s=psize)
ax6.scatter([w[0] for w in whlpl ], [w[1] for w in whlpl ], s=psize)

if fdist != '-':
	dist = read_float_list(basedir + '/' + fdist)
	ax4.hist(dist, 100)
	ax4.set_title('Pre-sleep log-ratio distribution')

plt.suptitle(basename[:-1].replace('_', ' ') + ', ST=' + str(speed_thold), fontsize = 20)
f.savefig(logdir + 'QUICK_CB_' + basename + '.png')

plt.show()
