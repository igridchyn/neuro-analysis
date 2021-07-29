#!/usr/bin/env python

# pull co-firing correlations from different days and do testing and plotting

from sys import argv
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from matplotlib import pyplot as plt
from call_log import log_call
from scipy.stats import pearsonr, spearmanr
from scipy.stats import norm
from iutils import *

if len(argv) < 7:
	print 'USAGE: (1)<session 1> (2)<session2> (3)<list of directories to look in> (4)<correlation type: c(pearson)/cr(rank)/pps(partial on presleep)/pft(partial first trial)> (5)<title addition> (6)<prefix of corrlist files>'
	print 'SESSION IDS: 2=LEARNING END, 3=NEW LEARNING START, 4=PRE-SLEEP(BEFORE) 5=FIRST TRIAL 6=POST-PROBE'
	print 'GROUP CO-FIRING CORRELATIONS FROM DIFFERENT DAYS FOR TESTING AND PLOTTING'
	exit(0)

log_call(argv)

S1 = int(argv[1])
S2 = int(argv[2])
TITADD = argv[5]

CL_PREF = argv[6]

CORTY = argv[4]
if CORTY not in ['c', 'pps', 'pft', 'cr']:
	print 'Correlation type should be one of the c / pps / pft'
	exit(1)

# common dataset: [ index of a group, control/target, learning correlation, post-learning correlation  ]

dirs = []
for line in open(argv[3]):
	if len(line) > 2:
		dirs.append(line[:-1])

print dirs

if len(dirs) < 21:
	print 'WARNING: less that 21 dirs'

ds = []
# read correlations and form a dataset
group = 0

NLOAD = 5
print 'WARNING: trying to load %d valeus from every corlist' % NLOAD

for dr in dirs:
	fab = open(dr + '/about.txt')
	for line in fab:
		if 'swap' in line:
			swap = int(line.split(' ')[-1])	
	#print 'SWAP = ', swap

	fcorre1 = open(dr + '/%s.corlist_e1' % CL_PREF)
	for line in fcorre1:
		crs = [float(f) for f in line.split(' ')]
		ds.append([group, swap])
		for i in range(NLOAD):
			ds[-1].append(crs[i])
		#ds.append([group, 0, crs[0], crs[1]])

	fcorre2 = open(dr + '/%s.corlist_e2' % CL_PREF)
	for line in fcorre2:
		crs = [float(f) for f in line.split(' ')]
		ds.append([group, 1-swap])
		for i in range(NLOAD):
			ds[-1].append(crs[i])
		#ds.append([group, 1, crs[0], crs[1]])
	
	group += 1

# print ds

ds = np.array(ds)
#i LAST =  'Fcor' - first trial correlations, not loaded in 1123 - FIX !!!
df = pd.DataFrame(data=ds, columns = ['Group', 'CT', 'Lcor', 'NLcor', 'PScor', 'FTcor', 'POcor'])

# ses_names = ['','','End of learning', 'Start of new learning', 'Pre-sleep: before', 'First trial', 'Post-probe']
ses_names = ['','','END OF LEARNING', 'START OF POST-LEARNING', 'PRE-SLEEP: BEFORE', 'First trial', 'POST-PROBE']

#print ds[-5:-1, :]

# ordered = False # only in new version : 0.21
#ct_catdat = pd.Categorical(ds[:,1], categories=[0, 1])
#df['CT'] = ct_catdat

# only in 0.21
df['CT'] = df['CT'].astype('category')
df['Group'] = df['Group'].astype('category')

# print df
# THIS GIVES ERROR IF NANs are USED ...
#md = smf.mixedlm("NLcor ~ Lcor + CT", df, groups=df["Group"])
##md = smf.mixedlm("NLcor ~ Lcor + CT", df, groups=df["Group"], re_formula="~ Lcor")
#md = smf.mixedlm("NLcor ~ Lcor + CT", df, groups=df["Group"], re_formula="~ 0 + Lcor + CT")
#mdf = md.fit()
#print mdf.summary()

# residuals - normal ?
# plt.hist(mdf.resid, 50)
# plt.show()

# ordinary least squares
print "OLS:"
ols = smf.ols('NLcor ~ Lcor + CT', data=df).fit()
print ols.summary()

# correlations of control and target
nind = ~np.isnan(ds[:,S1]) & ~np.isnan(ds[:,S2])

#idxf = ds[:,S1] < 0.15

idx_con = (ds[:,1] > 0.5) & nind #& idxf
idx_targ = (ds[:,1] < 0.5) & nind #& idxf
n_con = np.sum(idx_con)
n_targ = np.sum(idx_targ)
print 'Number of samples: %d con %d targ' % (n_con, n_targ)

# NORMAL CORRELATIONS
if CORTY == 'c':
	cc_con =  np.corrcoef(ds[idx_con,  S1], ds[idx_con,  S2])[0,1]
	cc_targ = np.corrcoef(ds[idx_targ, S1], ds[idx_targ, S2])[0,1]
elif CORTY == 'pps':
# PARTIAL - pre-sleep
	#print 'WARNING: partial correlations used, conditioned on the sleep correlations'
	cc_con = partial_correlation(ds[idx_con, S1], ds[idx_con, S2], ds[idx_con, 3])
	cc_targ = partial_correlation(ds[idx_targ, S1], ds[idx_targ, S2], ds[idx_targ, 3])
elif CORTY == 'pft':
	# PARTIAL - first trials
	print 'WARNING: partial correlations used, conditioned on the first learning trial'
	cc_con = partial_correlation(ds[idx_con, S1], ds[idx_con, S2], ds[idx_con, 4])
	cc_targ = partial_correlation(ds[idx_targ, S1], ds[idx_targ, S2], ds[idx_targ, 4])
elif CORTY == 'cr':
	cc_con =  spearmanr(ds[idx_con,  S1], ds[idx_con,  S2])[0]
	cc_targ = spearmanr(ds[idx_targ, S1], ds[idx_targ, S2])[0]

# plot scatter
#plt.figure()
#plt.scatter(ds[idx_con, S1], ds[idx_con, S2])

#plt.figure()
#plt.scatter(ds[idx_targ, S1], ds[idx_targ, S2], color = 'red')
#plt.show()

n_con = np.sum(idx_con)
n_targ = np.sum(idx_targ)
print 'CC cont/targ: %f / %f' % (cc_con, cc_targ)
print 'N con/targ: %d / %d' % (n_con, n_targ)
z_cc_con = np.arctanh(cc_con)
z_cc_targ = np.arctanh(cc_targ)
print 'Z con/targ: %.3f/%.3f' % (z_cc_con, z_cc_targ)

r_std_con_low = norm.sf(z_cc_con - 1.0/np.sqrt(n_con-3))
r_std_con_up = norm.sf(z_cc_con + 1.0/np.sqrt(n_con-3))
r_std_targ_low = norm.sf(z_cc_targ - 1.0/np.sqrt(n_targ-3))
r_std_targ_up = norm.sf(z_cc_targ + 1.0/np.sqrt(n_targ-3))

[r_std_con_low, r_std_con_up] = corr_conf_interval(cc_con, n_con)
[r_std_targ_low, r_std_targ_up] = corr_conf_interval(cc_targ, n_targ)

print 'Correlations of control / target : %.2f / %.2f' % (cc_con, cc_targ)
print 'Uppter / lower bounds R CON: %.3f / %.3f' % (r_std_con_low, r_std_con_up)
print 'Uppter / lower bounds R TARG: %.3f / %.3f' % (r_std_targ_low, r_std_targ_up)

z_obs = (z_cc_con - z_cc_targ) / np.sqrt(1.0/(n_con - 3) + 1.0/(n_targ - 3))
p_z = norm.sf(np.abs(z_obs))
print 'Z of control VS. target : %f, p-value = %e' % (z_obs, p_z)

nsqr_con = np.sqrt(n_con)
nsqrt_targ = np.sqrt(n_targ)

bs = np.array([0, 1])
bw = 0.4

#plt.figure(figsize = (5,8), dpi=92.88)
plt.figure(figsize = (7.5,10))

plt.bar(0, cc_con, width = bw)
plt.bar(1, cc_targ, width = bw, color = 'red')
tshift = 0.1
fs = 20
# DEBUG ONLY
#plt.text(0 + tshift, cc_con/2, str(n_con), fontsize=fs)
#plt.text(1 + tshift, cc_targ/2, str(n_targ), fontsize=fs)
plt.errorbar(bs + bw/2, [cc_con, cc_targ], yerr = [[r_std_con_low, r_std_targ_low], [r_std_con_up, r_std_targ_up]], linewidth=10, fmt = 'o', color='black')
giv = '' if CORTY in ['c', 'cr'] else ('given ' + ('first trial' if CORTY == 'pft' else 'pre-sleep (before)'))

# DEBUG VERSION
#plt.title('%so-firing correlations: %s vs.\n%s %s, p = %e\n%s' % ('C' if CORTY=='c' else ('Rank order c' if CORTY=='cr' else 'Partial c'), ses_names[S1], ses_names[S2], giv, p_z, TITADD))
#plt.title('%s VS.\n %s' % (ses_names[S1], ses_names[S2]), fontsize=30)
plt.title(TITADD, fontsize=30)

if S2 == 6:
	plt.ylim([0, 0.13])
else:
	plt.ylim([0, 0.3])

# plt.legend(['CONTROL', 'TARGET'])
plt.grid()
plt.xticks([0+bw/2, 1+bw/2], ['CONTROL', 'TARGET'], fontsize=25)

set_yticks_font(25)

plt.xlim([-0.2, 1.6])

plt.savefig('/home/igor/resim/_AUTOSAVE/CC-WAKING_%s' % TITADD)
plt.show()
