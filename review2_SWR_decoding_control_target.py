#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats

if len(argv) < :
	print 'USAGE: (1)<> (2)<> (3)<>'
	exit(0)

con = np.loadtxt(argv[1])
tar = np.loadtxt(argv[2])

# high confidence thresholds for control and target, likelihood is thresholded- defined from the distribution of the pre-sleep
thcon = float(argv[3])
thtar = float(argv[4])


