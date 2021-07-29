#!/usr/bin/env python

from tracking_processing import whl_to_pos, whl_to_speed
from sys import argv
import numpy as np
from iutils import *

if len(argv) < 7:
	print 'Arguments: (1)<dir with all.clu/res> (2)<whl file> (3)<firing rate factor threshold> (4)<env border> (5)<speed threshold> (6)<fr thold>'
	print 'Output: lists of cells for each environment'
	exit(0)

argv = resolve_vars(argv)

whl_path = argv[2]
whl = whl_to_pos(open(whl_path), False)
speed = whl_to_speed(whl)
frthold = float(argv[6])

print whl[0]

clu = [int(c) for c in open(argv[1] + whl_path.replace('whl','clu'))]
res = [int(c) for c in open(argv[1] + whl_path.replace('whl','res'))]

speed_thold = float(argv[5])
envbord = float(argv[4])
ratefac = float(argv[3])
nclu = max(clu)

envocc = [0, 0]

# calculate environment occupancy based on speed threshold - in whl samples
for t in range(len(whl)):
	if speed[t] < speed_thold or whl[t] == 0:
		continue
	env = whl[t][0] > envbord
	envocc[env] += 1	

spikes = np.zeros((nclu + 1, 2))
for i in range(len(clu)):
	t = res[i]
	if speed[t / 480] < speed_thold or whl[t / 480] == 0:
		continue
	env = whl[t / 480][0] > envbord
	spikes[clu[i], env] += 1

cells1 = []
cells2 = []
occfac = envocc[0] / float(envocc[1])

secs1 = envocc[0] / 50
secs2 = envocc[1] / 50

for c in range(2, nclu + 1):
	if (spikes[c,1] == 0 and spikes[c,0] > 0 or spikes[c, 0] / float(spikes[c, 1]) / occfac >= ratefac) and spikes[c, 0] / secs1 > frthold:
		cells1.append(c)
	if (spikes[c,0] == 0 and spikes[c,1] > 0 or spikes[c, 1] / float(spikes[c, 0]) * occfac >= ratefac) and spikes[c, 1] / secs2 > frthold:
		cells2.append(c)

print 'Selective cells (1/2):'
print cells1
print cells2
print 'Env occ: ', envocc
#print spikes
