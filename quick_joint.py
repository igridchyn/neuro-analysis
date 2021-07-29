#!/usr/bin/env python3

from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np
from sys import argv
from scipy import stats
from iutils_p3 import *
from numpy.polynomial.polynomial import polyfit

if len(argv) < 2:
    print('USAGE: <1>(values 1) <2>(values 2) [t: transform(exp) xl yl; ff: filtering file]')
    print('Display statisitics of the joint distributions of the 2 values')
    exit(0)

if len(argv) > 2 and os.path.isfile(argv[1]) and os.path.isfile(argv[2]):
	pdic = parse_optional_params(argv[3:])
else:
	pdic = parse_optional_params(argv[2:])

print(pdic)

if 'ff' in pdic:
    indf = np.loadtxt(pdic['ff'])
    indf = indf.astype(int)
    indf = indf.astype(bool)

#print 'WARNING: 0 ignored'
#x = [float(f) for f in open(argv[1]) if float(f) != 0]
#y = [float(f) for f in open(argv[2]) if float(f) != 0]

if len(argv) > 2 and os.path.isfile(argv[1]) and os.path.isfile(argv[2]):
	x = [float(f) for f in open(argv[1])]
	y = [float(f) for f in open(argv[2])]
else:
	d = np.loadtxt(argv[1])
	x = d[:,0]
	y = d[:,1]


#x = [float(f) for f in open(argv[1]) if len(f) > 1]
#y = [float(f) for f in open(argv[2]) if len(f) > 1]

# normal distribution center at x=0 and y=5
#x = np.random.randn(100000)
#y = np.random.randn(100000) + 5

x = np.array(x)
y = np.array(y)

mn = min(min(x), min(y))
mx = max(max(x), max(y))
plt.scatter(x,y)
#plt.plot([mn,mx], [mn,mx], color='black')
LFS = 20
if 'xl' in pdic: plt.xlabel(pdic['xl'], fontsize=LFS)
if 'yl' in pdic: plt.ylabel(pdic['yl'], fontsize=LFS)
if 'ti' in pdic: plt.title(pdic['ti'], fontsize=LFS)
plt.show()
print('WARNING: early exit')
print('Signed rank paired Wilcoxon test:', stats.wilcoxon(x, y))
print('Paired t-test:', stats.ttest_rel(x, y))
print('Mann-Whitney U-test:', stats.mannwhitneyu(x, y))
print('Shapiro:', stats.shapiro(x), stats.shapiro(y))
print('Shapiro, log:', stats.shapiro(np.log(x)), stats.shapiro(np.log(y)))
print('Paired t-test, log:', stats.ttest_rel(np.log(x), np.log(y)))
exit(0)

ind = ~np.isnan(x) & ~np.isnan(y) & (np.abs(np.log(x/y)) < 5)
x = x[ind]
y = y[ind]

if 'ff' in pdic:
    indf = indf[ind]

# y = np.exp(y)

# test if value > 0
#ytest = y[x > 0.25]
#ttestres = stats.ttest_1samp(ytest, 0)
#print 't-test for y:', ttestres

trans = gdv(pdic, 't')
if trans == 'exp':
	x = np.exp(x)
	y = np.exp(y)
	print('WARNING: EXP')

# print 'WARNING: > 0'
# ind = (x<0) & (y<0)
#ind = (x>0) & (y>0)
#x = x[ind]
#y = y[ind]

# TEST SIGNED-RANK PAIRED WILCOXON TEST

# PL
LFS = 25
#ratescores = [np.log(x[i]/y[i]) for i in range(len(x)) if y[i] > 0.05 and x[i] > 0.05]
#ratescores = [x[i]/y[i] for i in range(len(x)) if y[i] > 0.05 and x[i] > 0.05]

# INTERNEURONS
#ratescores = [(x[i]-y[i])/(y[i]+x[i]) for i in range(len(x)) if y[i] > 20 and x[i] > 20]
# PYRAMIDALS
ratescores = [(x[i]-y[i])/(y[i]+x[i]) for i in range(len(x)) if y[i] > 0.05 and y[i] < 20 and x[i] > 0.05 and x[i] < 20]

#bins = 10**np.arange(-1.5,1.5,0.04)
#plt.xscale('log')
print(np.mean(ratescores))
plt.xlabel('Rate score', fontsize=LFS)
plt.ylabel('Count', fontsize=LFS)
plt.hist(ratescores, bins=10)#bins)
#plt.title('Interneurons', fontsize=LFS+5)
plt.title('Pyramidal', fontsize=LFS+5)
strip_axes(plt.gca())
plt.show()
# exit(0)

#print 'Signed rank paired Wilcoxon test:', stats.wilcoxon(x[ind], y[ind])

b,a = polyfit(x,y,1)
print('POLYFIT:', b,a)

cc = np.ma.corrcoef(x, y)[0,1]
print('Correlation:', cc)

# print x,y
#colcode = [i/float(len(x)) for i in range(len(x))]
if 'ff' not in pdic:
    colcode = ['red' if (x[i] > 20 or y[i] > 20) and (x[i] > 15 and y[i] > 15) else 'b' for i in range(len(x))]
else:
    colcode = ['red' if indf[i] else 'blue' for i in range(len(x))]

colcode = np.array(colcode)
#plt.scatter(x, y,s=10, c=colcode)
plt.scatter(x[colcode == 'red'], y[colcode=='red'], color='red')
plt.scatter(x[colcode != 'red'], y[colcode!='red'], color='b')
plt.legend(['Interneuons', 'Pyramidals'], fontsize=20, loc='lower right')
plt.plot([min(min(x),min(y)), max(max(x), max(y))], [min(min(x),min(y)), max(max(x), max(y))], color='black')
#plt.xlabel('Light-OFF firing rates', fontsize=LFS)
plt.ylabel('Regular pulses firing rates', fontsize=LFS)
#plt.ylabel('% of HSE in REM sleep', fontsize=LFS)
plt.xlabel('Pre-sleep firing rates', fontsize=LFS)
plt.title('Correlation: %.3f' % cc, fontsize=25)
# POLYFIT
# plt.plot([min(x), max(x)], [b+a*min(x), b+a*max(x)], color='black')
#plt.grid()
lfs = 30
if 'xl' in pdic:
	plt.xlabel(pdic['xl'], fontsize = lfs)
if 'yl' in pdic:
	plt.ylabel(pdic['yl'], fontsize = lfs)
strip_axes(plt.gca())
plt.show()

xmin = x.min()
xmax = x.max()
ymin = y.min()
ymax = y.max()
X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
positions = np.vstack([X.ravel(), Y.ravel()])
kernel = stats.gaussian_kde(np.vstack([x, y]))
Z = np.reshape(kernel(positions).T, X.shape)
print(Z.shape)
plt.imshow(np.rot90(Z), extent=[xmin, xmax, ymin, ymax])
plt.scatter(x, y, s = 0.2)

mmi = max(xmin, ymin)
mma = min(xmax, ymax)
#plt.plot([xmin, xmax], [ymin, ymax])
plt.plot([mmi, mma], [mmi, mma])

#plt.hist2d(x, y, bins=nbins) #, norm=LogNorm())
#plt.colorbar()

plt.gca().set_xlim([xmin, xmax])
plt.gca().set_ylim([ymin, ymax])

plt.show()

x = np.array(x)
y = np.array(y)

print('x > y: %.2f%%' % (float(np.sum(x > y)) / len(x) * 100))
