#!/usr/bin/env python2

# read output of the summary_cellwise_light_effect (multiple files) and plot sipmple figures
from sys import argv
from matplotlib import pyplot as plt
from call_log import *
import numpy as np
from iutils import *
from scipy.stats import ttest_ind_from_stats
import Tkinter as Tk

def relabel(sig, v1, v2):
	return sig if sig != 'n.s.' else ('>' if v1 > v2 else '<')

if len(argv) < 4:
	print 'USAGE: (1)<output for the light ocnidiont> (2)<output for the non-light condition> (3)<index of the group to use for plotting>'
	print 'READ OUTPUT OF summary_cellwise_light_effect AND PLOT'
	exit(0)

ops = parse_optional_params(argv[4:])

dr = log_call(argv)
log_file(dr, argv[1])
log_file(dr, argv[2])
log_file(dr, argv[1] + '.combcorrs')
log_file(dr, argv[2] + '.combcorrs')

fsuml = open(argv[1])
fsumnl = open(argv[2])
IDX = int(argv[3])

# combcorrs - other measures
flc = open(argv[1] + '.combcorrs')
fnlc = open(argv[2] + '.combcorrs')
flc.readline()
flc.readline()
# line 3
ll = flc.readline()
fnlc.readline()
fnlc.readline()
# line 3
lnl = fnlc.readline()

for i in range(IDX):
	fsuml.readline()
	fsuml.readline()
	fsuml.readline()
	# rate scores
	fsuml.readline()
	
	fsumnl.readline()
	fsumnl.readline()
	fsumnl.readline()
	# rate scores
	fsumnl.readline()

# line rates light before
lrlb = fsuml.readline()
# line rates light after
lrla = fsuml.readline()

# line rates no light before
lrnlb = fsumnl.readline()
# line rates no light after
lrnla = fsumnl.readline()

# skip correlations
fsuml.readline()
fsumnl.readline()

# read scores
lscoresl = fsuml.readline()
lscoresnl = fsumnl.readline()
[cscore_lm, tscore_lm, cscore_lstd, tscore_lstd] = [float(w) for w in lscoresl.split(' ')]
[cscore_lm, tscore_lm, cscore_lstd, tscore_lstd] = [float(w) for w in lscoresl.split(' ')]
[cscore_nlm, tscore_nlm, cscore_nlstd, tscore_nlstd] = [float(w) for w in lscoresnl.split(' ')]
[cscore_nlm, tscore_nlm, cscore_nlstd, tscore_nlstd] = [float(w) for w in lscoresnl.split(' ')]

for i in range(6):
	flc.readline()
	fnlc.readline()

call_l  =  flc.readline()
call_nl = fnlc.readline()


print 'WARINING : lresp defined from parameters of summary_cle'
sumresp = call_l.split(' ')[5]
if ':' in sumresp:
        lresp = 'UNAFFECTED'
elif sumresp == '0':
        lresp = 'ALL'
elif float(sumresp) < 0:
        lresp = 'INHIBITED'
else:
        lresp = 'DISINHIBITED'


bw = 0.5
LFS = 30
if len(ll) > 0 and len(lnl) > 0:
	plt.figure(figsize=(10,7))

	vl = line_to_floats(ll)
	vnl = line_to_floats(lnl)
	plt.bar([1, 3], [vnl[0], vl[0]], width = bw)
	plt.bar([2, 4], [vnl[1], vl[1]], width = bw, color='red')
	plt.legend(['Control', 'Target'], fontsize=LFS, loc=5)

	# confidence interval
	vl_c_ci = corr_conf_interval(vl[0], int(vl[2]))
	vl_t_ci = corr_conf_interval(vl[1], int(vl[3]))
	vnl_c_ci = corr_conf_interval(vnl[0], int(vnl[2]))
	vnl_t_ci = corr_conf_interval(vnl[1], int(vnl[3]))

	plt.errorbar([1+bw/2, 3+bw/2], [vnl[0], vl[0]], yerr = [[vnl_c_ci[0], vl_c_ci[0]], [vnl_c_ci[1], vl_c_ci[1]]], color='black', linewidth=4, fmt='.')
	plt.errorbar([2+bw/2, 4+bw/2], [vnl[1], vl[1]], yerr = [[vnl_t_ci[0], vl_t_ci[0]], [vnl_t_ci[1], vl_t_ci[1]]], color='black', linewidth=4, fmt='.')

	#plt.legend(['CONTROL', 'TARGET'])
	#plt.xticks([1.3,2.3,3.3,4.3], ['NINH CON', 'NINH TARG', 'INH CON', 'INH TARG'], fontsize=18)
	plt.xticks([1.7, 3.7], ['Control HSE', 'Disrupted HSE'], fontsize=LFS)
	set_yticks_font(LFS)

	plt.xlim([0.5, 5])
	plt.ylim([0, 1.0])
	plt.grid()

	sh = 0.03
	ysh = 0.01
	print 'WARNING: hard-coded SIG STR IS USED'
	#plot_sig(1+bw/2, 2+bw/2, max(vnl[0], vnl[1]) + 0.07, sh, '*', 20, ysh)
	#plot_sig(1+bw/2, 3+bw/2, max(vnl[0], vnl[1]) + 0.14, sh, '****', 20, ysh)
	plot_sig(1+bw/2, 4+bw/2, max(vnl[0], vnl[1]) + 0.21, sh, '****', 20, ysh)

	plt.ylabel('Correlation of mean rates, r', fontsize = 30)

	# compare correltions with z-test
	p_con = ztest(vl[0], vnl[0], int(vl[2]), int(vnl[2]))
	print 'Mean correlations z-test: control in INH vs control in NINH:', p_con
	p_targ = ztest(vl[1], vnl[1], int(vl[3]), int(vnl[3]))
	print 'Mean correlations z-test: target in INH vs target in NINH:', p_targ
	p_ninh = ztest(vnl[0], vnl[1], int(vnl[2]), int(vnl[3]))
	print 'Mean correlations z-test: control in NINH vs target in NINH:', p_ninh
	p_self = ztest(vl[1], vnl[0], int(vl[3]), int(vnl[2]))
	print 'Mean correlations z-test: target in INH vs control in NINH:', p_self

	tsuf = gdv(ops, 't', '')
	#plt.title('Correlations of mean rates before and after' + ('' if len(tsuf) == 0 else (', ' + tsuf)) + ', ' + lresp)
	plt.subplots_adjust(left=0.13, right=0.98, bottom=0.08, top=0.96)
	plt.show()
	#plt.subplots_adjust(left=0.2)
	 

wl = call_l.split(' ')
wnl = call_nl.split(' ')

subl = ' '.join(wl[3:7]) + ' ' + str(IDX)
subnl = ' '.join(wnl[3:7]) + ' ' + str(IDX)

if subl != subnl:
	print 'ERROR: different calls were used to produce the summary ouput'
	exit(2)

# now can add the cle file used (diffdrent for inh and ninh)
subl = wl[2] + ' ' + subl
subnl = wl[2] + ' ' + subnl

print call_l

info_light_before = np.array([float(f) for f in lrlb.split(' ')])
info_light_after = np.array([float(f) for f in lrla.split(' ')])
info_nolight_before = np.array([float(f) for f in lrnlb.split(' ')])
info_nolight_after = np.array([float(f) for f in lrnla.split(' ')])

rates_light_before = info_light_before[:2]
rates_light_after = info_light_after[:2]
rates_nolight_before = info_nolight_before[:2]
rates_nolight_after = info_nolight_after[:2]
std_light_before = info_light_before[2:4]
std_light_after = info_light_after[2:4]
std_nolight_before = info_nolight_before[2:4]
std_nolight_after = info_nolight_after[2:4]
n_light_before = info_light_before[4:]
n_light_after = info_light_after[4:]
n_nolight_before = info_nolight_before[4:]
n_nolight_after = info_nolight_after[4:]
sem_light_before = std_light_before / np.sqrt(n_light_before)
sem_light_after = std_light_after / np.sqrt(n_light_after)
sem_nolight_before = std_nolight_before / np.sqrt(n_nolight_before)
sem_nolight_after = std_nolight_after / np.sqrt(n_nolight_after)

p_light_before = ttest_ind_from_stats(rates_light_before[0], std_light_before[0], n_light_before[1], rates_light_before[1], std_light_before[1], n_light_before[1], equal_var = False)
p_light_after = ttest_ind_from_stats(rates_light_after[0], std_light_after[0], n_light_after[1], rates_light_after[1], std_light_after[1], n_light_after[1], equal_var = False)
p_nolight_before = ttest_ind_from_stats(rates_nolight_before[0], std_nolight_before[0], n_nolight_before[1], rates_nolight_before[1], std_nolight_before[1], n_nolight_before[1], equal_var = False)
p_nolight_after = ttest_ind_from_stats(rates_nolight_after[0], std_nolight_after[0], n_nolight_after[1], rates_nolight_after[1], std_nolight_after[1], n_nolight_after[1], equal_var = False)

sig_light_before = p_to_sig_str(ttest_ind_from_stats(rates_light_before[0], std_light_before[0], n_light_before[1], rates_light_before[1], std_light_before[1], n_light_before[1], equal_var = False)[1])
sig_light_after = p_to_sig_str(ttest_ind_from_stats(rates_light_after[0], std_light_after[0], n_light_after[1], rates_light_after[1], std_light_after[1], n_light_after[1], equal_var = False)[1])
sig_nolight_before = p_to_sig_str(ttest_ind_from_stats(rates_nolight_before[0], std_nolight_before[0], n_nolight_before[1], rates_nolight_before[1], std_nolight_before[1], n_nolight_before[1], equal_var = False)[1])
sig_nolight_after = p_to_sig_str(ttest_ind_from_stats(rates_nolight_after[0], std_nolight_after[0], n_nolight_after[1], rates_nolight_after[1], std_nolight_after[1], n_nolight_after[1], equal_var = False)[1])

print 'P-values (light before, light after, nolight before, nolight after) :', p_light_before[1], p_light_after[1], p_nolight_before[1], p_nolight_after[1]

print rates_light_before, rates_light_after, rates_nolight_before, rates_nolight_after

# append diff sigs to file
fout = open('CLE_SUM.out', 'a')
fout.write('%100s' % (subl + ', ' + lresp + '         '))
msig_light_before = relabel(sig_light_before, rates_light_before[0], rates_light_before[1])
msig_light_after = relabel(sig_light_after, rates_light_after[0], rates_light_after[1])
msig_nolight_before = relabel(sig_nolight_before, rates_nolight_before[0], rates_nolight_before[1])
msig_nolight_after = relabel(sig_nolight_after, rates_nolight_after[0], rates_nolight_after[1])
fout.write('%5s%5s%5s%5s\n' % (msig_light_before, msig_light_after, msig_nolight_before, msig_nolight_after))
#exit(0)

bw = 0.8
# control light condition
balabs = ['BEFORE', 'AFTER']
clabs = ['CONTROL', 'TARGET']

print 'Numbers of cells: light / no light', n_light_before, n_nolight_before

# RATE SCORES
cscore_lsem  = cscore_lstd  / np.sqrt(n_light_before)
cscore_nlsem = cscore_nlstd / np.sqrt(n_nolight_before)
tscore_lsem  = tscore_lstd  / np.sqrt(n_light_before)
tscore_nlsem = tscore_nlstd / np.sqrt(n_nolight_before)
fig2= plt.figure()
ax1 = plt.gca()
ax1.set_title('Firing rate B-A scores, ' + lresp)
ax1.bar((1,5), (cscore_lm, cscore_nlm))
ax1.bar((2,6), (tscore_lm, tscore_nlm), color='r')
#ax1.text(1+bw, max([cscore_lm, tscore_lm, cscore_nlm, cscore_nlm])+max([cscore_lstd, cscore_nlstd, tscore_lstd, tscore_nlstd]))
#ax1.text(5+bw, max(rates_light_after)+max(sem_light_after), sig_light_after)
ax1.legend(clabs, loc='best')
ax1.errorbar((1+bw/2,5+bw/2), (cscore_lm, cscore_nlm), yerr =  (cscore_lsem, cscore_nlsem), fmt = '.', color='black')
ax1.errorbar((2+bw/2,6+bw/2), (tscore_lm, tscore_nlm), yerr =  (tscore_lsem, tscore_nlsem), fmt = '.', color='black')
plt.xticks([2,6], ['Light', 'No light'], fontsize = 20)



#fig, (ax1, ax2) = plt.subplots(1,2)
fig, ax1 = plt.subplots(1,1, figsize=(4,8))
fig2, ax2 = plt.subplots(1,1, figsize=(4,8))

ax1.set_title('Firing rates in light condition')
ax1.bar((1,5), (rates_light_before[0], rates_light_after[0]))
ax1.bar((2,6), (rates_light_before[1], rates_light_after[1]), color='r')
ax1.text(1+bw, max(rates_light_before)+max(sem_light_before), sig_light_before)
ax1.text(5+bw, max(rates_light_after)+max(sem_light_after), sig_light_after)
#ax1.legend(clabs, loc='best')
ax1.legend(clabs, loc=2)
ax1.errorbar((1+bw/2,5+bw/2), (rates_light_before[0], rates_light_after[0]), yerr =  (sem_light_before[0], sem_light_after[0]), fmt = '.', color='black')
ax1.errorbar((2+bw/2,6+bw/2), (rates_light_before[1], rates_light_after[1]), yerr =  (sem_light_before[1], sem_light_after[1]), fmt = '.', color='black')
sp = subl.find(' ')
subl1 = subl[:sp] + '\n' + subl[sp:]

#ax1.set_title(subl1 + ', ' + lresp, fontsize=15)
ax1.set_title(lresp + ' CELLS', fontsize=15)

#ax2.set_title('Firing rates in no light condition')
#ax2.set_title(subl1.replace('inh_top20', 'ninh') + ', ' + lresp, fontsize=15)
#ax2.set_title(subl1.replace('inh', 'ninh') + ', ' + lresp, fontsize=15)
ax2.set_title(lresp + ' CELLS', fontsize=15)

ax2.bar((1,5), (rates_nolight_before[0], rates_nolight_after[0]))
ax2.bar((2,6), (rates_nolight_before[1], rates_nolight_after[1]), color='r')
ax2.text(1+bw, max(rates_nolight_before)+max(sem_nolight_before), sig_nolight_before)
ax2.text(5+bw, max(rates_nolight_after)+max(sem_nolight_after), sig_nolight_after)
#ax2.legend(clabs, loc='best')
ax2.legend(clabs, loc=2)
ax2.errorbar((1+bw/2,5+bw/2), (rates_nolight_before[0], rates_nolight_after[0]), yerr =  (sem_nolight_before[0], sem_nolight_after[0]), fmt = '.', color='black')
ax2.errorbar((2+bw/2,6+bw/2), (rates_nolight_before[1], rates_nolight_after[1]), yerr =  (sem_nolight_before[1], sem_nolight_after[1]), fmt = '.', color='black')

xt1 = 2
xt2 = 6
xtfs = 18
ax2.set_xticks((xt1, xt2))
ax2.set_xticklabels(balabs, fontsize = xtfs)
ax1.set_xticks((xt1, xt2))
ax1.set_xticklabels(balabs, fontsize = xtfs)

ylfs = 20
ax1.set_ylabel('Z-scored firing rate', fontsize = ylfs)
ax2.set_ylabel('Z-scored firing rate', fontsize = ylfs)
ax1.yaxis.set_label_coords(-0.05, 0.5)
ax2.yaxis.set_label_coords(-0.05, 0.5)

#plt.suptitle(subl + ', ' + lresp, fontsize=15)
# plt.suptitle(subl1)

ymin = -0.5
ymax = 4

yl1 = ax1.get_ylim()
yl2 = ax2.get_ylim()
ymin = min(yl1[0], yl2[0])
ymax = max(yl1[1], yl2[1])

#ax1.set_ylim([ymin, ymax])
#ax2.set_ylim([ymin, ymax])
ymax=10
ax1.set_ylim([-0.5, ymax])
ax2.set_ylim([-0.5, ymax])

plt.legend(loc='best')

plt.show()
plt.margins(0,0)
fig.show()
fig2.show()
Tk.mainloop()
