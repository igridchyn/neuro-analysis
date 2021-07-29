#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats
from sklearn.linear_model import LinearRegression
from scipy.stats.stats import pearsonr 

if len(argv) < 2:
	print('USAGE: (1)<File with columns: dependepnt variable, independent variable, control variables>')
	exit(0)

d = np.loadtxt(argv[1])

# correlation of residuals
predbase = LinearRegression().fit(d[:,2:], d[:,1].reshape(-1,1)).predict(d[:,2:]) 
resbase = predbase - d[:,1].reshape(-1,1)
predall = LinearRegression().fit(d[:,2:], d[:,0].reshape(-1,1)).predict(d[:,2:]) 
resall = predall - d[:,0].reshape(-1,1)

#print(predbase[:2,:], d[:2,1], resbase[:2,:])

#print(regbase[:,0])
#print(regall)

#print('Normal:', np.corrcoef(d[:,0], d[:,1])[0,1])
#print('Partial', pearsonr(resbase[:,0], resall[:,0]))

r = pearsonr(resbase[:,0], resall[:,0])[0]
n = len(resall[:,0])
se = corr_conf_interval(r,n)[1]

print(r,se)

#fig, axar = plt.subplots(1,2)
#axar[0].scatter(resbase, resall)
#axar[1].scatter(d[:,0], d[:,1])
#plt.show()
