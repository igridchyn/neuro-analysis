#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from iutils import *
from call_log import *
from scipy import stats
from scipy.stats import mannwhitneyu, ttest_ind, wilcoxon

if len(argv) < 3:
	print 'USAGE: (1)<b/a rates in NINH events - disinhibited cells> (2)<b/a/ rates in NINH events - inhibited cells>'
	exit(0)

fsumnol_dinh = open(argv[1])
fsumnol_inh = open(argv[2])

# IDX = 0 for inh, 10 for DINH
for i in range(4*10):
        fsumnol_inh.readline()

# line rates no light before
lrnlb_inh = fsumnol_inh.readline()
# line rates no light after
lrnla_inh = fsumnol_inh.readline()

# line rates no light before
lrnlb_dinh = fsumnol_dinh.readline()
# line rates no light after
lrnla_dinh = fsumnol_dinh.readline()

# IN CASE OF RATES WRITTEN TO FILE
rawrates= [[float(f) for f in line.split(' ') if f != '\n'] for line in [lrnlb_inh, lrnla_inh, lrnlb_dinh, lrnla_dinh]]
# split lines into c/t
raw_rates = []
ns = []
for rawrate in rawrates:
        n1 = int(rawrate[0])
        raw_rates.append([rawrate[1:n1+1], rawrate[n1+2:]])
        ns.append([n1, len(rawrate)-n1-2])

# raw_rates is:
# [[lrnlb_inh_CON, lrnlrb_inh_TARG], [lrnla_inh_CON, lrnla_inh_TARG], [lrnlb_dinh_CON, lrnlb_dinh_TARG], [lrnla_dinh_ CON, lrnla_dinh_TARG]]]

rates = [[np.mean(rr[0]), np.mean(rr[1])] for rr in raw_rates]
stds = [[np.std(rr[0]), np.std(rr[1])] for rr in raw_rates]
ns = [[len(rr[0]), len(rr[1])] for rr in raw_rates]

print 'Compare inh before vs. inh. after, all cells (no split CON/TARG): INH / DINH', wilcoxon(rawrates[0], rawrates[1]), wilcoxon(rawrates[2], rawrates[3])
print 'Compare inh before vs. inh. after, CONTROL cells : INH / DINH', wilcoxon(raw_rates[0][0], raw_rates[1][0]), wilcoxon(raw_rates[2][0], raw_rates[3][0])
print 'Compare inh before vs. inh. after, TARGET cells : INH / DINH', wilcoxon(raw_rates[0][1], raw_rates[1][1]), wilcoxon(raw_rates[2][1], raw_rates[3][1])

# CHECK
DEBUG = False
if DEBUG:
    xb_c = np.array((0,3,7,10))
    xb_t = xb_c + 1
    plt.bar(xb_c, [rates[i][0] for i in range(4)])
    plt.bar(xb_t, [rates[i][1] for i in range(4)], color = 'r')
#plt.show() # FOR DEBUGGING ONLY

# NOW CALCULATE SCORES - separately for control and target cells
# raw_rates contains 4 X lists with 2 elements: list of control and target env. cell rates in one of the 4 conditions (b/a, inh/dinh)

scores = []
# inhibited/disinhibited cells
for sh in [0, 2]:
    # control/target cells
    for e in [0,1]:
        scores.append([raw_rates[sh+1][e][i] - raw_rates[sh][e][i] for i in range(len(raw_rates[sh][e]))])
        # scores.append([(raw_rates[sh+1][e][i] - raw_rates[sh][e][i])/(raw_rates[sh+1][e][i] + raw_rates[sh][e][i]) for i in range(len(raw_rates[sh][e]))])

# compare scores : for control cells, for target cells, and together
# scores = [ inh cells con, inh cells targ, dinh cells con, dinh cells targ ]

# add all
scores.append(scores[0] + scores[1])
scores.append(scores[2] + scores[3])

#print scores[0], scores[2]

print 'Mean, std, n CON cells', np.mean(scores[0]), np.std(scores[0]), len(scores[0]), np.mean(scores[2]), np.std(scores[2]), len(scores[2])
print 'Mean, std, n TARG cells', np.mean(scores[1]), np.std(scores[1]), len(scores[1]), np.mean(scores[3]), np.std(scores[3]), len(scores[3])
print 'Mean, std, n ALL cells', np.mean(scores[0]+scores[1]), np.std(scores[0]+scores[1]), len(scores[0]+scores[1]), np.mean(scores[2]+scores[3]), np.std(scores[2]+scores[3]), len(scores[2]+scores[3])
print 'Comapre scores of CON inh cells vs. CON dinh cells', mannwhitneyu(scores[0], scores[2])
print 'Comapre scores of TARG inh cells vs. TARG dinh cells', mannwhitneyu(scores[1], scores[3])
print 'Comapre scores of ALL inh cells vs. ALL dinh cells', mannwhitneyu(scores[1]+scores[0], scores[2] + scores[3])

tcon = mannwhitneyu(scores[0], scores[2])[1]
ttar = mannwhitneyu(scores[1], scores[3])[1]
tall = mannwhitneyu(scores[4], scores[5])[1]
ps = [tcon, ttar, tall]

# PLOT
x_inh = np.array([0, 3 ,6])
x_dinh = x_inh+1
plt.bar(x_inh, [np.mean(scores[i]) for i in [0, 1, 4]])
plt.bar(x_dinh, [np.mean(scores[i]) for i in [2, 3, 5]], color='red')
plt.xticks(x_inh+0.2, ['Control cells','Target cells','All cells'], fontsize=25)
plt.yticks([0, 0.4, 0.8, 1.2], fontsize=20)
plt.ylabel('Change in z-scored rate\nbefore-to-after', fontsize=25)
plt.legend(['Inhibited cells', 'Disinhibited cells'], fontsize=15, loc='center right')
plt.errorbar(x_inh, [np.mean(scores[i]) for i in [0, 1, 4]], yerr=[np.std(scores[i])/np.sqrt(len(scores[i])) for i in [0, 1, 4]], color='black', fmt='.')
plt.errorbar(x_dinh, [np.mean(scores[i]) for i in [2, 3, 5]], yerr=[np.std(scores[i])/np.sqrt(len(scores[i])) for i in [2, 3, 5]], color='black', fmt='.')
strip_axes(plt.gca())

for i in range(3):
    plt.text(x_inh[i], 1.2, p_to_sig_str(ps[i]), fontsize=25)

plt.show()









