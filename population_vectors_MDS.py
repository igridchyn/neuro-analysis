#!/usr/bin/env python

import os
from sys import argv
import numpy
from matplotlib import pyplot
from sklearn import manifold
from sklearn.metrics import euclidean_distances
import numpy as np
import random
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from iutils_p3 import read_float_list, write_list, read_int_list

if len(argv) < 8:
	print('Usage: ' + argv[0] + ' (1)<pop vecs 1> (2)<pop vecs 1 classes or -> (3)<pop vecs 2> (4)<pop vecs classes 2 or -> (5)<MDS output basename> (6)<max MDS vectors> (7)<dims>')
	exit(0)

OLDLOAD = False

if OLDLOAD:
    classes = []
    popvecs = []

    fpv1 = open(argv[1])
    noclass1 = True
    if argv[2] != '-':
        noclass1 = False
        class1 = [int(c) for c in open(argv[2]) if len(c) > 0]

    i = 0
    for l in fpv1:
        popv = [float(c) for c in l.split(' ')[:-1] if len(c) > 0]
        if len(popv) > 0:
            popvecs.append(popv)
            if noclass1:
                classes.append(0)
            else:
                classes.append(class1[i])
            i += 1

    print('Loaded %d vectors from the first file' % len(popvecs))

    fpv2 = open(argv[3])
    noclass2 = True
    if argv[4] != '-':
        noclass2 = False
        class2 = [int(c) + max(class1) + 1 for c in open(argv[2]) if len(c) > 0]
    else:
        class2 = max(classes) + 1

    i = 0
    for l in fpv2:
        popv = [float(c) for c in l.split(' ')[:-1] if len(c) > 0]
        if len(popv) > 0:
            popvecs.append(popv)
            if noclass2:
                classes.append(class2)
            else:
                classes.append(class2[i])
            i += 1
    print('Total number of vectors: %d' % len(popvecs))
    print('Length of classes: %d' % len(classes))

    popvecs = np.array(popvecs)
else:
    data = np.load(argv[1])
    popvecs = data['pops']
    classes = data['envs']


maxmdspop = int(argv[6])
if popvecs.shape[0] > maxmdspop:
	print('Subsampled %d vectors out of %d' % (maxmdspop,popvecs.shape[0]))
	inds = np.array(random.sample(range(0, popvecs.shape[0]), maxmdspop))
	popvecs = popvecs[inds,:]
	classes = np.array(classes)[inds]

dims = int(argv[7])
mdspath = argv[5] + '_' + argv[6] + '_' + argv[7] + '.mds.npz'
if os.path.isfile(mdspath):
    # OLD READING WAY
	#pos = np.array(read_float_list(mdspath))
	#classes = np.array(read_int_list(mdspath + '.classes'))
    mds_data = np.load(mdspath)
    pos = mds_data['pos']
    classes = mds_data['classes']

    print('Read MDS pos from ' + mdspath)
    print('Size of read points array: ' + str(pos.shape))
	# print classes
else:
	print('Start MDS...')
	seed = np.random.RandomState(seed=3)
	similarities = euclidean_distances(popvecs)
	print('Done similarities')
	# max_iter defgault = 300
	# eps default = 1e-6
	mds = manifold.MDS(n_components = dims, max_iter=300,random_state=seed,dissimilarity='precomputed', n_jobs=-1,n_init=1, eps=1e-6)
	pos = mds.fit(similarities).embedding_
	print('Done MDS...')
 
	np.savez(mdspath, pos=pos, classes=classes)
   
    # OLD WRITE WAY
#	fmds = open(mdspath, 'w')
#	for p in pos:
#		if dims == 2:
#			fmds.write('%f %f\n' % (p[0], p[1]))
#		elif dims == 3:
#			fmds.write('%f %f %f\n' % (p[0], p[1], p[2]))
#	fmds.close()
#	print('Saved MDS to %s' % mdspath)
#	write_list(list(classes), mdspath + '.classes')

# pyplot.scatter(pos[:,0], pos[:,1], c=classes, cmap='Set1', s=30)

print('pos shape:', pos.shape)
cmax = max(classes)
print(cmax)
classes = classes.reshape((1,-1))[0]
print(classes)

colors = ['gold', 'red', 'cyan', 'black']
if dims == 3:
	fig = pyplot.figure()
	ax = fig.add_subplot(111, projection = '3d')
for i in range(0, cmax + 1):
    ind = classes == i
#    print(ind.reshape(1,-1))
    if dims == 2:
        pyplot.scatter(pos[ind,0], pos[ind,1], c=colors[i], s=30)
    else:
        ax.scatter(pos[ind,0], pos[ind,1], pos[ind,2], c=colors[i], s=30)

pyplot.legend(['Env1', 'Env2', 'Sleep C1', 'Sleep C2'])
pyplot.show()
