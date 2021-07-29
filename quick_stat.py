#!/usr/bin/env python3

from numpy.polynomial.polynomial import polyfit
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
import statsmodels as sm
import statsmodels.distributions
#from iutils_p3 import *

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['font.family'] = 'sans-serif'

if len(argv) < 2:
	print('Usage: (1)<file with 1 column of numbers> (2)<limit in format [g|l]<number> or 0 or -> [xl - x label; yl - ylabel; st - stat (ELB/P20/P80) f - filter file] ')
	exit(0)

# log_call(argv)
# print 'WARNING: no call logging!'

if len(argv) > 3:
	pdic = parse_optional_params(argv[3:])
else:
	pdic = {}

uselim = False
if len(argv) > 2 and argv[2] != '-':
	uselim = True
	lim = float(argv[2][1:] if argv[2][0] in 'gl' else argv[2])
	limless = argv[2][0] == 'l'
	# print 'USE LIMIT'
	PRNT = False

PRNT = True
if 'st' in pdic:
	stat = pdic['st']
	if stat not in ['ELB', 'P20', 'P80' 'PPP', 'P50']:
		print('last argument can be one of: ELB, P20, P80, PPP')
		exit(0)
	STAT = stat
	PRNT = False
else:
	STAT = ''

data = []
nanc = 0
if argv[1].endswith('npy'):
    data = np.load(argv[1])
else:
    for a in open(argv[1]).read().split('\n'):
            #print a
            if len(a) > 0 :
                    try:
                            # if not np.isnan(float(a)) and abs(float(a)) > 0.0000001: # ????
                            if not np.isnan(float(a)):
                                    #data.append(np.exp(float(a)))
                                    data.append(float(a))
                            else:
                                    nanc += 1
                    except:
                            if PRNT:
                                    print('Skip line ', a	)

if PRNT:
	print('%d/%d nan data points' % (nanc, nanc + len(data)))
	print('Data min/max: %f / %f' % (min(data), max(data)))

data = np.array(data)
NDAT = float(len(data))

#print '% of data < 0.4, 0.5, 0.6:', np.sum(data < 0.4) / float(len(data)), np.sum(data < 0.5) / float(len(data)), np.sum(data < 0.6) / float(len(data))
#exit(0)

# filter
if 'f' in pdic:
    filt = np.loadtxt(pdic['f'])
    # INTERNEURONS - RATE FILTER
    #data = data[filt > 25]
    # PYRAMIDALS - RATE FILTER
    #data = data[filt < 20]

if uselim:
        #print 'WARNING: LIMMIT NOT FILTERING, JSUT COUNTING !'
        #print '%% DATA>LIM: %.2f' % (np.sum(data > lim) / float(len(data)))
        print((np.sum(data > lim) / float(len(data))))
	#data = data[data < lim] if limless else data[data > lim]
        #exit(0)

#PERCENTILES
for i in range(0, 100, 5):
    print('Percentile %d %% : %.2f' % (i, np.percentile(data, i)))

#data = 1 - data
print('Mean/Std', np.mean(data), np.std(data))
#exit(0)

# BOX PLOT
BOX = False
if BOX:
    plt.figure(figsize=(3.5,5))
    plt.boxplot(data, boxprops= dict(linewidth=3.0, color='black'), whiskerprops=dict(linestyle='-',linewidth=3.0, color='black'))
    plt.yticks([0,0.25,0.5, 0.75,1], fontsize=25)
    #plt.gca().locator_params(nbins=5, axis='y')
    #plt.ylabel('HSE in REM, % of all HSE', fontsize=25)
    #plt.ylabel('HSE in Non-theta, % of all HSE', fontsize=25)
    plt.ylabel('Disrupted HSE in Non-theta\n% of all disrupted HSE', fontsize=25)
    #plt.title('% ')
    plt.xticks([])
    strip_axes(plt.gca())
    plt.subplots_adjust(left=0.37, bottom=0.04, right=0.97, top=0.97)
    plt.show()
    #exit(1)

# RAW DATA WITH FIT LINE
#b,a = polyfit(range(len(data)), data, 1)
plt.plot(data)
#plt.plot([0, len(data)], [b, b + a*len(data)], color='black')
FSLAB = 20
#plt.xlabel('Sleep time, min', fontsize = FSLAB)
#plt.ylabel('SWR frequency, Hz', fontsize = FSLAB)
#plt.grid()
plt.show()

exit(0)

# SMOOTHED:
#data = data[~np.isinf(data)]
#data = data[data != 0]
#smw = 50
#datasm =np.convolve(np.abs(data), [1] * smw) # 50-fluctuations; 350-smooth for rt conf
#plt.plot(datasm[smw:-smw])
#plt.show()

#print 'WARNING: PRELIMINARY EXIT'
#exit(0)

STACKBAR = False
# STACK BAR
if STACKBAR:
    fr_inh = np.sum(data < 0.75) / NDAT
    fr_dinh = np.sum(data > 1.5) / NDAT
    p1 = plt.bar(0, fr_inh)
    p2 = plt.bar(0, fr_dinh, bottom = fr_inh, color = 'red')
    p3 = plt.bar(0, 1-fr_inh-fr_dinh, bottom = fr_inh+fr_dinh, color='black')
    plt.legend((p1[0], p2[0], p3[0]), ('Inhibited', 'Disinhibited', 'Unaffected'), fontsize=30)
    plt.xlim([-0.2, 1.0])
    plt.ylim([0, 1.3])
    plt.xticks([], [])
    set_yticks_font(30)
    plt.yticks([0, 0.25, 0.5, 0.75, 1.0])
    plt.gca().get_yaxis().set_ticks_position('left')
    plt.show()

#print 'WARNING: EXP'
#data = np.exp(data)

print('Size after filtering: %d' % len(data))

mean = np.mean(data)
std = np.std(data)

if PRNT:
	print('Data mean / std: %.2f / %.2f' % (mean, std))
	print('Mean exp: %.3f' % (np.exp(mean)))
	
	logbins = np.logspace(-3,3,100)

        # % REM
        #rbins = [0.075, 0.15, 0.225, 0.3, 0.375]
        #rbins = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
        #hs = plt.hist(data, bins=rbins, rwidth=0.8)
	plt.hist(data, bins=logbins) # 100

        
        # RESONSE
        #rbins = np.arange(-2, 2, 0.5)
        #rbins = np.logspace(-2, 2, 10)
	#hs = plt.hist(np.exp(data), bins=rbins) # 100

        #plt.xticks(rbins[::2])
        #plt.title('Interneurons', fontsize = 25)
	plt.title('Pyramidal', fontsize = 25)
        #plt.gca().set_xscale('log')
        #plt.xticks(hs[1][::3])

	#plt.grid()
	#plt.axvline(x=0, color = 'r')


	LFS = 25
	plt.xlabel('% REM', fontsize=LFS)
	plt.ylabel('Number of sessions', fontsize = LFS)

	lfs = 25
	print(pdic)
	if 'xl' in pdic:
		plt.xlabel(pdic['xl'], fontsize = lfs)
		#plt.xlabel('Decoding\nconfidence', fontsize = lfs)
		plt.subplots_adjust(bottom=0.2)
	if 'yl' in pdic:
		plt.ylabel(pdic['yl'], fontsize = lfs)

	set_xticks_font(lfs)
	set_yticks_font(lfs)

        # IF LOG HIST IS USED
	plt.xscale("log")

	#plt.subplots_adjust(bottom=0.21, right=0.97, top=0.95, left=0.21)
	strip_axes(plt.gca())
	plt.tight_layout()
	plt.show()

if PRNT:
	print('Data median : %.2f' % np.median(data))

#plt.hist(data[data > 30], 400)
plt.hist(data, 400)
plt.show()

ecdf = statsmodels.distributions.ECDF(data)
if PRNT:
	plt.plot(ecdf.x, ecdf.y, linewidth=5)
	plt.xlabel('% of REM', fontsize=15)
	plt.ylabel('CDF', fontsize=15)
	#plt.axvline(x=0, color = 'r')
	#plt.grid()
	plt.show()
	exit(0)

	# bar + points + stderr
	b = 0.1
	plt.bar(0, mean, width=b, alpha = 0.3)
	plt.errorbar(b/2, mean, yerr = std, linewidth=5, alpha = 0.3)
	plt.scatter([b/2] * len(data), data, color='black', s=50)
	plt.show()

if STAT == 'ELB':
	dy = np.zeros(ecdf.y.shape,np.float)
	dy[0:-1] = np.diff(ecdf.y)/np.diff(ecdf.x)
	dy[-1] = (ecdf.y[-1] - ecdf.y[-2])/(ecdf.x[-1] - ecdf.x[-2])
	weights = [0.1, 0.2, 0.4, 0.2, 0.1]
	dy = np.convolve(dy, weights, 'same')

	if PRNT:
		plt.plot(ecdf.x, dy)
		plt.show()

	i=0
	while i < len(dy) and dy[i] < 0.5 or np.isinf(dy[i]):
		i += 1
	print(ecdf.x[i])
elif STAT == 'P20':
	print(np.percentile(data, 20))
elif STAT == 'P80':
	print(np.percentile(data, 80))
elif STAT == 'PPP':
	print('45   percentile:', np.percentile(data, 45))
	print('59.5 percentile:', np.percentile(data, 59.5))

lev0 = 0
while lev0 < len(ecdf.x)-1 and ecdf.x[lev0] < 0:
	lev0 += 1

if PRNT:
	print('0 level percentile: %.2f\n' % (ecdf.y[lev0] * 100))
	for i in range(0, 100, 5):
		print('Percentile %d %% : %.2f' % (i, np.percentile(data, i)))

# split of data : < -A, > A, in [-A, A] - for cell response quantification
splits = [[], [], []]
tholds = []
for thold in np.sort(np.abs(data)):
	less = np.sum(data < - thold) / float(len(data))
	more = np.sum(data > thold) / float(len(data))
	unaff = 1.0 - less - more
	splits[0].append(less)
	splits[1].append(unaff)
	splits[2].append(more)
	tholds.append(thold)

plt.stackplot(tholds, splits) #, labels = ['INHIBITED', 'UNAFFECTED', 'DISINHIBITED'])
plt.xlim([0, 3])
plt.xlabel('Threshold')
plt.ylabel('Proportion')
plt.title('Proportion of light-affected cells from threshold')
plt.legend()
plt.show()
