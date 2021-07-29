#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
import os
from iutils import *
import numpy as np
from scipy.stats import pearsonr
from call_log import *

def read_pfs(path):
	# to avoid duplicating the filtration process - load the pfs_summary output
	fpfsmeans = open(path)

	# skip until desired measure
	for i in range(PFSM):
		# multiple values
		nv1 = int(fpfsmeans.readline())
		for i in range(nv1):
			fpfsmeans.readline()
		nv2 = int(fpfsmeans.readline())
		for i in range(nv2):
			fpfsmeans.readline()
		# if mean only
		# fpfsmeans.readline()

	# ! validate con / targ order

	tmp_meanpfs_t = []
	tmp_meanpfs_c = []
	# multiple values ...
	nvt = int(fpfsmeans.readline())
	for i in range(nvt):
		tmp_meanpfs_t.append(float(fpfsmeans.readline()))
	nvc = int(fpfsmeans.readline())
	for i in range(nvc):
		tmp_meanpfs_c.append(float(fpfsmeans.readline()))
	# if means only
	# meanpfs.append([float(f) for f in fpfsmeans.readline().split(' ')])

	tmp_meanpfs_c = np.array(tmp_meanpfs_c)
	tmp_meanpfs_t = np.array(tmp_meanpfs_t)

	# VALUES ARE ALREADY FILTERED
	#ipath_c = os.path.dirname(path) + 'C_8.ind'
	#ipath_t = os.path.dirname(path) + 'T_8.ind'
	#ind_c = read_bool_array(ipath_c)
	#ind_t = read_bool_array(ipath_t)
	#print ind_c.shape, tmp_meanpfs_c.shape
	
	return tmp_meanpfs_c, tmp_meanpfs_t

def read_firing_rates(path1, path2):
	# CLE files
	rinh = read_float_array(path1)
	rninh = read_float_array(path2)

	# magnitude of rate change
	#return np.abs(np.log(rinh[:,4] / rinh[:,3])), np.abs(np.log(rninh[:,4] / rninh[:,3]))
	return rinh[:, 6], rninh[:, 6]

def read_cofcorrs(path1, path2):
	cc1 = read_float_array(path1)
	cc2 = read_float_array(path2)
	#print cc1, cc2
	#return cc1[:,PFSM], cc2[:,PFSM]
	if CCMPART > 0:
		return partial_correlation(cc1[:,PFSM], cc1[:,COFCORM], cc1[:,CCMPART]), partial_correlation(cc2[:,PFSM], cc2[:,COFCORM], cc2[:,CCMPART])
	else:
		return np.ma.corrcoef(cc1[:,PFSM], cc1[:,COFCORM])[0,1], np.ma.corrcoef(cc2[:,PFSM], cc2[:,COFCORM])[0,1]

def read_goal_dists(path):
	gd = read_float_array(path)

	return gd[:,6]-gd[:,4], gd[:,7]-gd[:,5]

NARG = 6
if len(argv) < NARG:
	print '(1)<list of directories> (2)<number of PFS measure to use : 0-7> (3)<behavioral measure to use: d10, d10s, d10_ls, trg, nc10, ftpl, prg> (4)<for CC - 2nd column> (5)<for CC - partial by>'
	print 'Plot behavioural measure versus PFS'
	exit(0)

ld = log_call(argv)

COFCORRS = False

PT_GD = 1
PT_CCW = 2
PT_PFS = 3
# firing rates before and after HSE detection
PT_R = 4
PT = PT_PFS

meanpfs = []
behmeas = []

meanpfs_c = []
meanpfs_t = []
behmeas_c = []
behmeas_t = []

BMEAS = argv[3]
PFSM = int(argv[2])
COFCORM = int(argv[4])
# partial cof corr by this column
CCMPART = int(argv[5])

startdir = os.getcwd()

MEANS = False

if COFCORRS and not MEAN:
	print 'ERROR: cannot do individual values for COF. CORRS'
	exit(1)

if PT == PT_GD: 
	print 'HARD-CODED GD FILE goal_dist_REV6_1_4.out'

listpath = argv[1]
for line in open(argv[1]):
	os.chdir(line[:-1] + '/..')

	# IF PFS
	if PT == PT_PFS:
		tmp_meanpfs_c, tmp_meanpfs_t = read_pfs('PFS_MEAN.txt')

	print os.getcwd()

	full = resolve_vars(['%{FULL}'])[0]

	# IF COFIRING CORELATIONS
	#tmp_meanpfs_1, tmp_meanpfs_2 = read_cofcorrs('NOSB_ST4_OCC5.corlist_e1', 'NOSB_ST4_OCC5.corlist_e2')
	#tmp_meanpfs_1, tmp_meanpfs_2 = read_goal_dists('goal_dist_REV6_1_4.out')
	tmp_meanpfs_i, tmp_meanpfs_ni = read_firing_rates('13ssi%s/inh_top20.100ms.z.d20.rep1.cle' % full, '13ssi%s/ninh.100ms.z.d20.rep1.cle' % full)

	if PT != PT_PFS and PT != PT_R:
		swap = bool(int(resolve_vars(['%{swap}'])[0]))
		if swap:
			tmp_meanpfs_c = tmp_meanpfs_1
			tmp_meanpfs_t = tmp_meanpfs_2
		else:
			tmp_meanpfs_c = tmp_meanpfs_2
			tmp_meanpfs_t = tmp_meanpfs_1	
		
		if PT == PT_GD:
			ipath_c = 'C_8.ind'
			ipath_t = 'T_8.ind'
			ind_c = read_bool_array(ipath_c)
			ind_t = read_bool_array(ipath_t)
			tmp_meanpfs_c = tmp_meanpfs_c[ind_c]
			tmp_meanpfs_t = tmp_meanpfs_t[ind_t]

	if PT == PT_R:
		ipath_c = 'C_8.ind'
		ipath_t = 'T_8.ind'
		ind_c = read_bool_array(ipath_c)
		ind_t = read_bool_array(ipath_t)
		tmp_meanpfs_c = tmp_meanpfs_ni[ind_c]
		tmp_meanpfs_t = tmp_meanpfs_i[ind_t]
		#tmp_meanpfs_c = tmp_meanpfs_ni
		#tmp_meanpfs_t = tmp_meanpfs_i
	
	if not COFCORRS:
		nvc = len(tmp_meanpfs_c)
		nvt = len(tmp_meanpfs_t)
	else:
		nvc=1
		nvt=1

	if MEANS:
		if not COFCORRS:
			meanpfs_t.append(np.nanmean(tmp_meanpfs_t))
			meanpfs_c.append(np.nanmean(tmp_meanpfs_c))
		else:
			meanpfs_t.append(tmp_meanpfs_t)
			meanpfs_c.append(tmp_meanpfs_c)
	else:
		meanpfs_t.extend(list(tmp_meanpfs_t))
		meanpfs_c.extend(list(tmp_meanpfs_c))


	# READ BEHAVIOUR
	vrs = resolve_vars(['%{animal}', '%{day}'])
	# read params
	animal = vrs[0]
	day = vrs[1]
	os.chdir(startdir)

	# open beh
	fbeh = open(line[:-1] + '/%s_%s_16l.whl.cbbeh' % (animal, day))
	
	for line in fbeh:
		ws = line.split(' ')
		if ws[0] == BMEAS:
			# target -> control
			# single value
			# behmeas.append([float(ws[2]), float(ws[1])])
			# multiple values
			if not MEANS:
				for i in range(nvt):
					behmeas_t.append(float(ws[2]))
				for i in range(nvc):
					behmeas_c.append(float(ws[1]))
			else:
				behmeas_t.append(float(ws[2]))
				behmeas_c.append(float(ws[1]))
		

os.chdir(startdir)

# corelation of combined set
# single values
#ameanpfs = np.array([m[0] for m in meanpfs] + [m[1] for m in meanpfs])
#abehmeas = np.array([b[0] for b in behmeas] + [b[1] for b in behmeas])
#ameanpfs_c = np.array([m[1] for m in meanpfs])
#abehmeas_c = np.array([b[1] for b in behmeas])
#ameanpfs_t = np.array([m[0] for m in meanpfs])
#abehmeas_t = np.array([b[0] for b in behmeas])

# multiple values
ameanpfs = np.array(meanpfs_c + meanpfs_t)
abehmeas = np.array(behmeas_c + behmeas_t)
ameanpfs_c = np.array(meanpfs_c)
ameanpfs_t = np.array(meanpfs_t)
abehmeas_c = np.array(behmeas_c)
abehmeas_t = np.array(behmeas_t)

#print 'WARNING: SCALED FTPL'
#if BMEAS == 'ftpl':
#	abehmeas /= 54.0
#	abehmeas_c /= 54.0
#	abehmeas_t /= 54.0
#	abehmeas += 1
#	abehmeas_c += 1
#	abehmeas_t += 1

LOG = (BMEAS == 'ftpl')
#LOG = False
#if LOG:
#	abehmeas = np.log(abehmeas)
#	abehmeas_c = np.log(abehmeas_c)
#	abehmeas_t = np.log(abehmeas_t)

#print 'WARNING: differences instead of CONTROL'
#abehmeas_c = abehmeas_c - abehmeas_t
#ameanpfs_c = ameanpfs_c - ameanpfs_t

ind = ~np.isnan(ameanpfs)
ind_c = ~np.isnan(ameanpfs_c)
ind_t = ~np.isnan(ameanpfs_t)

print ind
print sum(ind)
corr = np.corrcoef(ameanpfs[ind], abehmeas[ind])[0, 1]
corr_c = np.corrcoef(ameanpfs_c[ind_c], abehmeas_c[ind_c])[0, 1]
corr_t = np.corrcoef(ameanpfs_t[ind_t], abehmeas_t[ind_t])[0, 1]
p_corr = pearsonr(ameanpfs[ind], abehmeas[ind])[1]
p_corr_c = pearsonr(ameanpfs_c[ind_c], abehmeas_c[ind_c])[1]
p_corr_t = pearsonr(ameanpfs_t[ind_t], abehmeas_t[ind_t])[1]
print 'CORR = %.3f, p=%.4f' % (corr, p_corr)
print 'CORR CON = %.3f, p=%.2f' % (corr_c, p_corr_c)
print 'CORR TARG = %.3f, p=%.4f' % (corr_t, p_corr_t)

plt.figure(figsize = (14, 11))

plt.scatter(abehmeas_t, ameanpfs_t, color = 'r')
#plt.scatter(abehmeas_c, ameanpfs_c, color = 'b')
fs = 40

meas_labs = ['', ', firing rates', '', '',  ', firing rates, selectivity', '','', ', firing rates (2 sessions)']
meas_lab = meas_labs[PFSM]
#beh_labs = {'d10':'Dwell time', 'ftpl':'First trial path length', 'nc10':'Number of crossings'}
#beh_labs = {'d10':'Dwell time', 'ftpl':'First trial path length', 'nc10':'Number of crossings'}
beh_labs = {'d10':'Dwell time proportion', 'ftpl':'First trial excess path length, cm', 'nc10':'Number of crossings'}
beh_lab = beh_labs[BMEAS]

# plt.ylabel('PFS: End of learning vs. first 2 trials of new learning\ncell filters: remapping' + meas_lab, fontsize = fs)
# plt.ylabel('PFS: END OF LEARNING VS. POST\ncell filters: remapping' + meas_lab, fontsize = fs)
CCLABS = ['L1-END', 'L2-START', 'PRESLEEP', 'FIRST TRIALS, L1', 'POST']
#ylab = 'COFIRING CORRELATION: %s VS. %s' % (CCLABS[PFSM], CCLABS[COFCORM])
#ylab = 'CHANGE IN DISTANCE TO GOAL'
if CCMPART > 0:
	ylab += ' PARTIAL BY %s' % CCLABS[CCMPART]

#ylab = 'PFS: end of learning vs. post-probe'
ylab = 'Correlation of firing rates (r)'
plt.ylabel(ylab, fontsize = fs+10)
#plt.ylabel(split2lines(ylab), fontsize = fs)

plt.xlabel(beh_lab, fontsize = fs+10)
if LOG:
	plt.gca().set_xscale('log')

# DEBUG
#plt.title('Corretations(joint/control/target): %.2f %.2f %.2f\np-values: %.4f %.4f %.4f' % (corr, corr_c, corr_t, p_corr, p_corr_c, p_corr_t))
plt.grid()
#plt.legend(['TARGET', 'CONTROL'], loc='best', fontsize=35)

set_xticks_font(30)
set_yticks_font(30)

plt.subplots_adjust(bottom=0.15)
plt.subplots_adjust(left=0.15)

title = ylab.replace(' ','_').replace(':','') + '_' + beh_lab.replace(' ', '_')
plt.savefig('/home/igor/resim/_AUTOSAVE/%s.png' % title)
plt.show()
