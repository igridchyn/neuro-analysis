#!/usr/bin/env python3

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils_p3 import *
#from call_log import *
from scipy import stats
import warnings

warnings.filterwarnings("ignore")

if len(argv) < 5:
    print('USAGE: (1)<base for PF> (2)<session1> (3)<session2> (4)<output file>')
    print('        COMPARE MEAN AND MAX FIRING RATES IN 2 ENVS, 2 SESSIONS + PFS')
    exit(0)

BASE = argv[1]
S1 = argv[2]
S2 = argv[3]
FN_OUT = argv[4]

dic = {}
for line in open('../../about.txt'):
    ws = line.split(' ')
    if len(ws) > 1:
        dic[ws[0]] = ws[1][:-1]

occ1 = np.loadtxt(BASE + 'occ_' + S1 + '.mat')
occ2 = np.loadtxt(BASE + 'occ_' + S2 + '.mat')

esplit = occ1.shape[1] // 2
print ('Env split', esplit)
#esplit = 25
#print('WARNING: ESPLIT OVERRIDE')

occ1[np.isinf(occ1)] = np.nan
occ2[np.isinf(occ2)] = np.nan
MINOCC = 3
occboth1 = (occ1[:,:esplit] > MINOCC) & (occ1[:,esplit:] > MINOCC)
occboth2 = (occ2[:,:esplit] > MINOCC) & (occ2[:,esplit:] > MINOCC)
print('OCCS BOTH PASSING, 1/2:', np.sum(occboth1), np.sum(occboth2))
occsboth = [occboth1, occboth2]

means = []
# change in abs score: abs(score1) - abs(score2)
meanscores = []
meanscores_both = []
meanscores_nonorm = []
maxscores = []
maxs = []
pfss = []

c = 1
while os.path.isfile(BASE + str(c) + '_' + S1 + '.mat'):
    pf1 = np.loadtxt(BASE + str(c) + '_' + S1 + '.mat') * 50
    pf2 = np.loadtxt(BASE + str(c) + '_' + S2 + '.mat') * 50
    pf1[np.isinf(pf1)] = np.nan
    pf2[np.isinf(pf2)] = np.nan

    pf1[np.isnan(pf2)] = np.nan
    pf2[np.isnan(pf1)] = np.nan
    nnn1 = ~np.isnan(pf1[:,:esplit]) & ~np.isnan(pf1[:,esplit:])
    nnn2 = ~np.isnan(pf2[:,:esplit]) & ~np.isnan(pf2[:,esplit:])

    nnn_e1 = ~np.isnan(pf1[:,:esplit]) & ~np.isnan(pf2[:,:esplit]) 
    nnn_e2 = ~np.isnan(pf1[:,esplit:]) & ~np.isnan(pf2[:,esplit:]) 

    efocc = np.nansum(occ1) / np.nansum(occ2)

    # session 1, split into env1 and 2
    pfs1 = [pf1[:,:esplit], pf1[:,esplit:]]
    # session 2, split into env1 and 2
    pfs2 = [pf2[:,:esplit], pf2[:,esplit:]]

    occ1_sum1 = np.sum(occ1[:,:esplit])
    occ1_sum2 = np.sum(occ1[:,esplit:])
    occ2_sum1 = np.sum(occ2[:,:esplit])
    occ2_sum2 = np.sum(occ2[:,esplit:])

    # WORKS BEST with 3
#    if max(np.nanmax(pf1), np.nanmax(pf2)) < 3:
#    if max(np.nanmax(pf1), np.nanmax(pf2)) < 1:
#    if min(np.nanmax(pf1), np.nanmax(pf2)) > 10:
#        c += 1
#        continue

#   means.append([np.nansum(pfs1[0] * occ1[:,:esplit])/occ1_sum1, np.nansum(pfs1[1] * occ1[:,esplit:])/occ1_sum2, np.nansum(pfs2[0] * occ2[:,:esplit] * efocc)/occ2_sum1, np.nansum(pfs2[1] * occ2[:,esplit:] * efocc)/occ2_sum2])
    means.append([np.nansum(pfs1[0] * occ1[:,:esplit])/occ1_sum1, np.nansum(pfs1[1] * occ1[:,esplit:])/occ1_sum2, np.nansum(pfs2[0] * occ2[:,:esplit])/occ2_sum1, np.nansum(pfs2[1] * occ2[:,esplit:])/occ2_sum2])

    mar = means[-1]
    meanscores.append(abs((mar[2]-mar[3])/(mar[2]+mar[3])) - abs((mar[0]-mar[1])/(mar[0]+mar[1])))
    meanscores_both.append([(mar[0]-mar[1])/(mar[0]+mar[1]), (mar[2]-mar[3])/(mar[2]+mar[3])])

    nnan_count = [np.sum(~np.isnan(a)) for a in [pfs1[0], pfs1[1], pfs2[0], pfs2[1]]]
    mar = [np.nanmean(pfs1[0]) / nnan_count[0], np.nanmean(pfs1[1]) / nnan_count[1], np.nanmean(pfs2[0]) / nnan_count[2], np.nanmean(pfs2[1]) / nnan_count[3]]
    meanscores_nonorm.append(abs((mar[2]-mar[3])/(mar[2]+mar[3])) - abs((mar[0]-mar[1])/(mar[0]+mar[1])))
    
    maxs.append([np.nanmax(pfs1[0]), np.nanmax(pfs1[1]), np.nanmax(pfs2[0]), np.nanmax(pfs2[1])])
    mar = maxs[-1]
    maxscores.append(abs((mar[2]-mar[3])/(mar[2]+mar[3])) - abs((mar[0]-mar[1])/(mar[0]+mar[1])))

#    if min(means[-1]) > 0.5:
#    if min(maxs[-1]) > 1:
    pfss.append([ np.ma.corrcoef(pfs1[0][occsboth[0] & nnn1], pfs1[1][occsboth[0] & nnn1])[0,1], np.ma.corrcoef(pfs2[0][occsboth[1] & nnn2], pfs2[1][occsboth[1] & nnn2])[0,1], np.ma.corrcoef(pfs1[0][nnn_e1], pfs2[0][nnn_e1])[0,1], np.ma.corrcoef(pfs1[1][nnn_e2], pfs2[1][nnn_e2])[0,1]])

    c += 1

# PLOT: differences in max / mean before and after + x = y line

means = np.array(means)
maxs = np.array(maxs)    
pfss = np.array(pfss)
meanscores = np.array(meanscores)
meanscores = np.reshape(meanscores, (-1,1))
meanscores_nonorm = np.array(meanscores_nonorm)
meanscores_nonorm = np.reshape(meanscores_nonorm, (-1,1))
meanscores_both = np.array(meanscores_both)
maxscores = np.array(maxscores)
maxscores = np.reshape(maxscores, (-1,1))
ids = np.reshape(np.array([int(dic['animal_id']), int(dic['day_id']), int(dic['paradigm_id'])]), (1, -1))
ids = np.repeat(ids, len(maxs), axis=0)

print(means.shape)
#print(means)

#print(pfss)
print('Mean pfs before / after %.2f / %.2f' % (np.nanmean(pfss[:,0]), np.nanmean(pfss[:,1])))

print('Mnea score change: before to after: %.2f' % (np.nanmean(meanscores)))

# WRITE ALL MEASURES AS MATRIX TO FILE
cmb = np.hstack((means, maxs, pfss, meanscores, maxscores, ids, meanscores_nonorm, meanscores_both))
np.savetxt(FN_OUT, cmb)
exit(0)

# PLOTTING
dbef = np.abs(means[:,0] - means[:,1])
daft = np.abs(means[:,2] - means[:,3])
print('Mean abs diffs before / after: %.2f / %.2f' % (np.mean(dbef), np.mean(daft)))
plt.scatter(dbef, daft, s=5)
plt.plot([min(dbef), max(dbef)], [min(dbef), max(dbef)], color='black')
plt.title('MEAN ABD DIFFS BEFORE / AFTER')
plt.show()

dbef = np.abs(maxs[:,0] - maxs[:,1])
daft = np.abs(maxs[:,2] - maxs[:,3])
print('Max abs diffs before / after: %.2f / %.2f' % (np.mean(dbef), np.mean(daft)))
plt.scatter(dbef, daft, s=5)
plt.plot([min(dbef), max(dbef)], [min(dbef), max(dbef)], color='black')
plt.title('MAX ABS DIFFS BEFORE / AFTER')
plt.show()

# LOGRAT
dbef = np.abs(np.log(means[:,0] / means[:,1]))
daft = np.abs(np.log(means[:,2] / means[:,3]))
dbef[np.isinf(dbef)] = np.nan
daft[np.isinf(daft)] = np.nan
print('Mean abs LOGRAT before / after: %.2f / %.2f' % (np.nanmean(dbef), np.nanmean(daft)))
plt.scatter(dbef, daft, s=5)
plt.plot([min(dbef), max(dbef)], [min(dbef), max(dbef)], color='black')
plt.title('MEAN ABD DIFFS BEFORE / AFTER')
plt.show()

dbef = np.abs(np.log(maxs[:,0] / maxs[:,1]))
daft = np.abs(np.log(maxs[:,2] / maxs[:,3]))
dbef[np.isinf(dbef)] = np.nan
daft[np.isinf(daft)] = np.nan
print('Max abs LOGRAT before / after: %.2f / %.2f' % (np.nanmean(dbef), np.nanmean(daft)))
plt.scatter(dbef, daft, s=5)
plt.plot([min(dbef), max(dbef)], [min(dbef), max(dbef)], color='black')
plt.title('MAX ABS DIFFS BEFORE / AFTER')
plt.show()

