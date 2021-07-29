#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt
from sys import argv
import statsmodels as sm
import statsmodels.distributions
from scipy.stats import ks_2samp, mannwhitneyu, ttest_ind, wilcoxon
from iutils_p3 import *
import os

def RGB(red,green,blue): return '#%02x%02x%02x' % (red,green,blue)

def plot_prep():
    strip_axes(plt.gca())
    if 'yl' in pdic: plt.ylabel(pdic['yl'], fontsize=25)
    if 'xl' in pdic: plt.xlabel(pdic['xl'], fontsize=25)
    if 'ti' in pdic: plt.title(pdic['ti'], fontsize=20)
    plt.tight_layout()


if len(argv) < 2:
	print('Usage: (1)<file with 1 column of numbers> (2)<2nd file> (3)<index file> [-l limit, -l1 label1 -l2 label2 -t title(appended)]')
	exit(0)

import matplotlib as mpl
#mpl.rcParams['font.sans-serif'] = 'Helvetica'
#mpl.rcParams['font.family'] = 'sans-serif'

print('\n\n')

#log_call(argv)

# parse the optional params
pdic = parse_optional_params(argv[3:])

lim = float(pdic['l']) if 'l' in pdic else 0

def read_data(path):
	data = []
	for a in open(path).read().split('\n'):
		#print a
		if len(a) > 0 :
			try:
				if not np.isnan(float(a)):
					data.append(float(a))
				else:
					nanc += 1
			except:
				# print 'Skip line ', a	
				pass
	return data

#if len(argv) > 2 and (not os.path.isfile(argv[1]) or not os.path.isfile(argv[2])):
#	print('ERROR: one of the inpit files does not exist')
#	exit(1)

if len(argv) >= 3 and os.path.isfile(argv[2]):
    nanc = 0
    data = read_data(argv[1])
    data2 = read_data(argv[2])
    data = np.array(data)
    data2 = np.array(data2)
else:
    print('Attmpt to read 2 columns from first file')
    data = np.loadtxt(argv[1])
    data2 = data[:,1]
    data = data[:,0]

inds = [] #if len(argv) < 4 or argv[3] == '-' else np.loadtxt(argv[3], dtype=float)

if len(inds) > 0:
    inds = inds.astype(int)
    inds = inds.astype(bool)
    inds = inds[:len(data)]
    
    # INVERT FOR PYRAMIDALS
    inds = ~inds

    print('WARNING: FILTER DATA WITH INDICES')

    print(len(inds), len(data), len(data2))

    data = data[inds]
    data2 = data2[inds]

print('Len after filt:', len(data), len(data2))

#print('FILTER BY RATE!')
#indf = (data > 0.5) & (data2 > 0.5)  & (data < 5) & (data2 < 5)
#indf = (data > 0.5) & (data2 < 5)  | (data2 > 0.5) & (data2 < 5)
#indf = (data > 0.5) & (data2 > 0.5)
#indf = (data > 25) & (data2 > 25)
#indf = (data > 30) & (data2 > 30)
#indf = (data > 30) & (data2 > 10)

# FOR LIGHT RESPONSE: ONLY TAKE THOSE WHICH HAVE HIGH IN DATA2 !!!
#indf = (data2 > 10) # & (data > 10)
#data = data[indf]
#data2 = data2[indf]


PLOT = False
# PLOTS
#print('WARNING: DIFF')
#data = data[1:] - data[:-1]
#data2 = data2[1:] - data2[:-1]
if PLOT:
    plt.plot(data)
    plt.plot(data2, color='red')
    plot_prep()
    plt.show()
    exit()

# BARS
#plt.figure(figsize=(4,6))
#plt.bar([0], np.mean(data))#, color=RGB())
#plt.bar([2], np.mean(data2))#, color='red')
#plt.legend(['Control HSE', 'Disrupted HSE'], fontsize=15)
#plt.errorbar([0], np.mean(data), yerr=np.std(data)/np.sqrt(len(data)), color='black', linewidth=4)
#plt.errorbar([2], np.mean(data2), yerr=np.std(data2)/np.sqrt(len(data)), color='black', linewidth=4)

# VERTICAL POINTS + LINES
plt.scatter([0]*len(data), data, color='black', zorder=1000)
plt.scatter([2]*len(data2), data2, color='black', zorder=1000)
# connect with lines [e.g. HSE Duration]
for i in range(len(data)):
    col = 'b' if data[i] > data2[i] else 'r'
    plt.plot([0, 2], [data[i], data2[i]], color = col)
plt.xticks([],[])
strip_axes(plt.gca())

plt.xlim(-0.5, 2.5)

if 'yl' in pdic: plt.ylabel(pdic['yl'], fontsize=25)
if 'xl' in pdic: plt.xlabel(pdic['xl'], fontsize=25)
#plt.ylabel('ABS rate discrimination score', fontsize=25)
#plt.ylabel('Binary deocding accuracy', fontsize=25)

if 'ti' in pdic: plt.title(pdic['ti'], fontsize=20)
#plt.title('LT + PLUS\nbefore < 0.2', fontsize=20)
#plt.title('ALL PARADIGMS', fontsize=25)
plt.tight_layout()
plt.show()
exit()

#plt.title('Interneurons', fontsize=25)
#plt.title('Abs scores', fontsize=25)

# plt.ylim([0, 1.35])

plt.xticks([],[])
strip_axes(plt.gca())
#plt.yticks([0, 25, 50, 75, 100])
set_yticks_font(20)
plt.subplots_adjust(left=0.29, bottom=0.03, right=0.96, top=0.92)

plt.gca().locator_params(nbins=5, axis='y')
plt.tight_layout()

plt.show()

if len(data) == len(data2):
	print('Correlation: %.3f' % np.corrcoef(data, data2)[0,1])

kst = ks_2samp(data, data2)
mwt = mannwhitneyu(data, data2)
tt  = ttest_ind(data, data2)

print('Mean values:, stds, ns', np.mean(data), np.mean(data2), np.std(data), np.std(data2), len(data), len(data2))
print('KS test: ',   kst)
print('MW U test: ', mwt )
print('T test: ', tt)

if len(data) == len(data2):
    print('Wilcoxon: ', wilcoxon(data, data2))

exit(0)
print('%d/%d nan data points' % (nanc, nanc + len(data)))

data = np.array(data)
data2 = np.array(data2)

if lim > 0:
	data = data[data < lim]

mean = np.mean(data)
std = np.std(data)
mean2 = np.mean(data2)
std2 = np.std(data2)
n1 = len(data)
n2 = len(data2)

print('Data 1 mean / std: %.2f / %.2f' % (mean, std))
print('Data 2 mean / std: %.2f / %.2f' % (mean2, std2))

#[n, bins,prts] =plt.hist(data, 300)
#plt.hist(data2, [b+0.5 for b in bins])
#plt.axvline(x=0, color = 'r')
#plt.show()

f, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 12))

SUBPL = True

nbins = 6 # 10
xmin = -0.5 # -0.6
xmax = 1.0
[hist1, be1] = np.histogram(data, bins=nbins, range=(xmin, xmax), normed = not SUBPL)
[hist2, be2] = np.histogram(data2, bins=nbins, range=(xmin, xmax), normed = not SUBPL)

hist1 = np.array(hist1)
hist2 = np.array(hist2)
hist1 = hist1 / float(np.sum(hist1))
hist2 = hist2 / float(np.sum(hist2))

print(len(hist1), len(hist2))

bindist = (xmax-xmin)/nbins

bc1 = [xmin + i * bindist for i in range(nbins)]
bc2 = [xmin + i * bindist for i in range(nbins)]

bw = 0.15
# 0.22 for POST, 0.3 for L2-START, 0.4 for L2-END
ymax = 0.35

if SUBPL:
	# 2 subplots
	ax1.bar(bc1, hist1, width = bw)
	ax2.bar(bc1, hist2, width = bw, color = 'red')
	#ax1.set_title(gdv(pdic, 'l1', argv[1]) + ' Mean=%.3f, N=%d' % (mean, n1))
	#ax2.set_title(gdv(pdic, 'l2', argv[2]) + ' Mean=%.3f, N=%d' % (mean2, n2))
	#ax1.set_title(gdv(pdic, 'l1', argv[1]), fontsize = 25)
	#ax2.set_title(gdv(pdic, 'l2', argv[2]), fontsize = 25)
	#ax1.grid()
	#ax2.grid()
	print('WARNING YLIM ENFORCED')

	strip_axes(ax1)
	strip_axes(ax2)

	ax1.set_ylim([0, ymax])
	ax2.set_ylim([0, ymax])

	ax1.locator_params(nbins=5, axis='y')
	ax2.locator_params(nbins=5, axis='y')

else:
	# on one 
	plt.bar(bc1, hist1, width = 0.04)
	plt.bar(bc2, hist2, width = 0.04, color = 'green')
	plt.legend([gdv(pdic, 'l1', argv[1]), gdv(pdic, 'l2', argv[2])])

ax1.text(-0.4, 0.2, 'CONTROL', fontsize=35)
ax2.text(-0.4, 0.2, 'TARGET', fontsize=35)
lfs = 35
#ax1.set_xlabel('Place field similarity (r)', fontsize=lfs)
ax2.set_xlabel('Place field similarity (r)', fontsize=lfs)
ax1.set_ylabel('Proportion', fontsize=lfs)
ax2.set_ylabel('Proportion', fontsize=lfs)

tfs = 25
set_xticks_font(tfs)
set_yticks_font(tfs)
plt.sca(ax1)
set_xticks_font(tfs)
set_yticks_font(tfs)

# DEBUG
#plt.suptitle(gdv(pdic, 't') + '\n KS: %.4f, MW: %.4f, T: %.4f' % (kst[1], mwt[1], tt[1]))
plt.suptitle(gdv(pdic, 't'), fontsize=30)
plt.show()

print('Data median : %.2f' % np.median(data))

# plt.hist(data[data > 30], 400)
# plt.show()

ecdf = statsmodels.distributions.ECDF(data)
ecdf2 = statsmodels.distributions.ECDF(data2)
plt.figure(figsize = (10, 8))
lw = 4
plt.plot(ecdf.x, ecdf.y, linewidth=lw)
plt.plot(ecdf2.x, ecdf2.y, color='red', linewidth=lw)
#plt.axvline(x=0, color = 'r')
plt.legend(['CONTROL', 'TARGET'], fontsize=30, loc='best')
lfs = 40
plt.ylabel('Probability', fontsize=lfs)
plt.xlabel('PFS', fontsize=lfs)
set_xticks_font(25)
set_yticks_font(25)
plt.subplots_adjust(top=0.83)
plt.subplots_adjust(bottom=0.13)
plt.title(gdv(pdic, 't').replace('VS.', 'VS.\n'), fontsize=lfs)
plt.grid()
plt.show()

lev0 = 0
while lev0 < len(ecdf.x) and ecdf.x[lev0] < 0:
	lev0 += 1

print('0 level percentile: %.2f\n' % (ecdf.y[lev0] * 100))

for i in range(0, 100, 5):
	print('Percentile %d %% : %.2f' % (i, np.percentile(data, i)))
