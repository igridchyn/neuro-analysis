#!/usr/bin/env python

from sys import argv
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import ttest_ind
from iutils import *
from call_log import log_call
from statsmodels.sandbox.stats.multicomp import multipletests

def corr_test(cc_con, n_con, cc_targ, n_targ):
	z_cc_con = np.arctanh(cc_con)
	z_cc_targ = np.arctanh(cc_targ)
	z_obs = (z_cc_con - z_cc_targ) / np.sqrt(1.0/(n_con - 3) + 1.0/(n_targ - 3))
	p_z = norm.sf(np.abs(z_obs))
	return [p_z, z_obs]

if len(argv) < 3:
	print 'USAGE: (1)<combcorrs file - inh> (2)<combcorrs file - ninh>'
	exit(0)

# OLD NORMAL - 4 GROUPS - INH-CON, INH-TARG, NINH-CON, NINH-TARG
vals = []
#for i in range(1, 5):
#	vals.append([float(f) for f in open(argv[i])])

ld = log_call(argv)

# 8 VALUES
# 2 pars
f1 = open(argv[1])
# LINE 1
line1 = f1.readline()
[c1i, c2i, n1i, n2i] = [float(f) for f in line1.split(' ')]

f2 = open(argv[2])
# LINE 1 correlations of before / after by environment
line2 = f2.readline()
[c1ni, c2ni, n1ni, n2ni] = [float(f) for f in line2.split(' ')]

# LINES 2-3 read rest if needed
for i in range(2):
	f1.readline()
	f2.readline()

# LINE 4 partial conditioned on learning end - inhibited / non-inhibited
[par_len_ci, par_len_ti, npar_len_ci, npar_len_ti] = [float(f) for f in f1.readline().split(' ')]
[par_len_cni, par_len_tni, npar_len_cni, npar_len_tni] = [float(f) for f in f2.readline().split(' ')]


# LINE 5 - cof. corrs with learning end - before and after for control / target
[plei_cb, plei_ca, plei_tb, plei_ta, nplei_cb, nplei_ca, nplei_tb, nplei_ta] = [float(f) for f in f1.readline().split(' ')]
[pleni_cb, pleni_ca, pleni_tb, pleni_ta, npleni_cb, npleni_ca, npleni_tb, npleni_ta] = [float(f) for f in f2.readline().split(' ')]


# LINE 6 partial cof. corr. of before and after given pre-sleep cofiring correlations (before or after - defined in summary_cellwise_effect)
[par_pres_ci, par_pres_ti, npar_pres_ci, npar_pres_ti] =  [float(f) for f in f1.readline().split(' ')]
[par_pres_cni, par_pres_tni, npar_pres_cni, npar_pres_tni] =  [float(f) for f in f2.readline().split(' ')]

# LINE 7
f1.readline()
f2.readline()

# LINE 8 correlations of reponse-grouped cofirings
[resp_ci,  nresp_ci]  = [float(f) for f in f1.readline().split(' ')]
[resp_cni, nresp_cni] = [float(f) for f in f2.readline().split(' ')]

# LINE 9 - correlations of combined co-firings of control / target vs end of learning - before and after
[bef_vs_lend_i, aft_vs_lend_i, nbef_vs_lend_i, naft_vs_lend_i] = line_floats(f1)
[bef_vs_lend_ni, aft_vs_lend_ni, nbef_vs_lend_ni, naft_vs_lend_ni] = line_floats(f2)

# LINE 10 - parameters ...
lpar1 = f1.readline()
lpar2 = f2.readline()
sumpars  = lpar1.split(' ')
spar = ' '.join(sumpars[-5:])

print 'WARINING : lresp defined from parameters of summary_cle'
sumresp = sumpars[5]
if ':' in sumresp:
	lresp = 'UNAFFECTED'
elif sumresp == '0':
	lresp = 'ALL'
elif float(sumresp) < 0:
	lresp = 'INHIBITED'
else:
	lresp = 'DISINHIBITED'

# line 11 - correlations of combined co-firings of control / target before/after light VS end of learning co-firing correlations in the opposite environment
[bef_vs_lend_op_i, aft_vs_lend_op_i, nbef_vs_lend_op_i, naft_vs_lend_op_i] = line_floats(f1)
[bef_vs_lend_op_ni, aft_vs_lend_op_ni, nbef_vs_lend_op_ni, naft_vs_lend_op_ni] = line_floats(f2)

# line 12 - correlations of before/after coifirings with end-of-learning co-firings in the other environment - as a control !
[bef_vs_lend_op_i, aft_vs_lend_op_i, d1, d2, nbef_vs_lend_op_i, naft_vs_lend_op_i, d3, d4] = line_floats(f1)
[bef_vs_lend_op_ni, aft_vs_lend_op_ni, d1, d2, nbef_vs_lend_op_ni, naft_vs_lend_op_ni, d3, d4] = line_floats(f2)

# =================================================================================================================================================================================================
# LINE 1 - NORMAL COF. CORR. OF BEFORE AND AFTER
#vals = [c1i, c2i, c1ni, c2ni]
#ns = [n1i, n2i, n1ni, n2ni]

# !!!!! ONLY VALID IF LISTS ARE JOINED IN THE SUMMARY SCRIPT
# CC OF B-A FOR COUPLES FROM JOINT C-T LIST, USE ONLY FIRST-VALID "CONTROL" LIST
#vals = [c1ni, c2i]
#ns = [n1ni, n1i]

# LINE 4 - PARTIAL CONDITIONED ON LEARNING END
#vals = [par_len_ci, par_len_ti, par_len_cni, par_len_tni]
#ns = [npar_len_ci, npar_len_ti, npar_len_cni, npar_len_tni]

# LINE 5 - WITH LEARNING END - BEFORE AND AFTER, CONTROL AND TARGET
vals = [plei_cb, plei_ca, plei_tb, plei_ta, pleni_cb, pleni_ca, pleni_tb, pleni_ta] 
ns = [nplei_cb, nplei_ca, nplei_tb, nplei_ta, npleni_cb, npleni_ca, npleni_tb, npleni_ta] 

# SUB - same environment 


# WITH LEARNING END - BEFORE AND AFTER, BUT FOR ALL COUPLES FROM JOINT (CONTROL, TARGET) CELL LIST
# OLD vals = [plei_cb, plei_ca, pleni_cb, pleni_ca] 
#vals = [pleni_cb, plei_cb,  pleni_ca, plei_ca] 
#ns = [nplei_cb, nplei_ca, npleni_cb, npleni_ca] 

# WITH LEARNING END - BEFORE AND AFTER, BUT FOR ALL COUPLES FROM JOINT (CONTROL, TARGET) CELL LIST + ALONG WITH CCs with the opposite environment
#vals = [pleni_cb, bef_vs_lend_op_ni, plei_cb, bef_vs_lend_op_i,  pleni_ca, aft_vs_lend_op_ni, plei_ca, aft_vs_lend_op_i] 
#ns = [nplei_cb, nbef_vs_lend_op_ni, nplei_ca, nbef_vs_lend_op_i, npleni_cb, naft_vs_lend_op_i, npleni_ca, naft_vs_lend_op_i] 

# PARTIAL OF BEFORE/AFTER CONDITIONED ON PRE-SLEEP (BEFORE OR AFTER - DEFINED IN SUMMARY_CLE)
#vals = [par_pres_ci, par_pres_ti, par_pres_cni, par_pres_tni]
#ns= [npar_pres_ci, npar_pres_ti, npar_pres_cni, npar_pres_tni]

# RESPONSE-GROUPED
# vals = [resp_cni, resp_ci]
# ns = [nresp_ci, nresp_cni]

# VS END OF LEARNING - CORRELATIONS OF COMBINED CONTROL AND TARGET CO-FIRING LISTS
#vals = [bef_vs_lend_ni, bef_vs_lend_i, aft_vs_lend_ni, aft_vs_lend_i]
#ns = [nbef_vs_lend_ni, nbef_vs_lend_i, naft_vs_lend_ni, naft_vs_lend_i]

# VS END OF LEARNING - COMBINED CONTROL AND TARGET, ALONG with the same but with end-of-learning co-firing correlations from the opposite environment
#vals = [bef_vs_lend_ni, bef_vs_lend_op_ni, bef_vs_lend_i, bef_vs_lend_op_i,aft_vs_lend_ni, aft_vs_lend_op_ni, aft_vs_lend_i, aft_vs_lend_op_i]
#ns = [nbef_vs_lend_ni, nbef_vs_lend_op_ni, nbef_vs_lend_i, nbef_vs_lend_op_i, naft_vs_lend_ni, naft_vs_lend_op_ni, naft_vs_lend_i, naft_vs_lend_op_i]

print 'Ns:', ns

# confidence intervals
cins = [corr_conf_interval(vals[i], ns[i]) for i in range(len(vals))]

if len(vals) == 8:
	b = [1,2,3,4,6,7,8,9]
else:
	b = range(len(vals))

# pairwise tests + p-value correction (multiple testing)
pinf = []
for i in range(len(vals)):
	for j in range(i):
		pinf.append([i, j] + corr_test(vals[i], ns[i], vals[j], ns[j]))
# correction
ps = [pi[2] for pi in pinf]
ps_corr = multipletests(ps, 0.05, method = 'bonferroni')[1]
for k in range(len(pinf)):
	pinf[k][2] = ps_corr[k]
	print 'P %d VS %d = ' % (pinf[k][0], pinf[k][1]), pinf[k][2:4]

#al2 = 0.35
al2 = 0.35 if len(vals) > 4 else 1
#colors = [(0,0,1), (1,0,0), (0,0,1,al2), (1,0,0,al2)] * 2
colors = [(0,0,1), (1,0,0), (0,0,0), (0.82,0.64,0.125)] * 2

# dum = [0.33, 0.43, 0.77, 0.21]

if len(vals) == 2:
	plt.figure(figsize = (3,7))
elif len(vals) == 4:
	plt.figure(figsize = (7, 10))
else:
	plt.figure(figsize = (16, 7))

bw = 0.3
# font size for number of data points
fs_n = 14
fs_ticks = 30
fs_leg = 20
plt.grid()
for i in range(len(vals)):
	plt.bar(b[i], np.mean(vals[i]), width=bw, color=colors[i])
	#plt.bar(b[i],  dum[i], width=bw, color=colors[i])

	# debug only
	#plt.text(b[i], vals[i]/2, str(int(ns[i])), fontsize=fs_n)

if len(vals) == 8:
	plt.legend(['CONTROL-BEFORE', 'CONTROL-AFTER', 'TARGET-BEFORE', 'TARGET-AFTER'], fontsize = fs_leg, loc = 'best')
else:
	plt.legend(['CONTROL', 'TARGET'], fontsize = fs_leg, loc = 'best')

for i in range(len(vals)):
	# for day-wise correlations
	#plt.errorbar(b[i] + bw/2, np.mean(vals[i]), yerr=np.std(vals[i]) / np.sqrt(len(vals[i])), linewidth = 3, color = 'black')

	# for combined correlations - need z-transform or confidence interval
	#plt.errorbar(b[i] + bw/2, np.mean(vals[i]), yerr=np.std(vals[i]) / np.sqrt(len(vals[i])), linewidth = 3, color = 'black')

	#plt.errorbar(b[i] + bw/2, dum[i], yerr=np.std(vals[i]) / np.sqrt(len(vals[i])), linewidth = 3, color = 'black')
	
	plt.errorbar(b[i] + bw/2, np.mean(vals[i]), yerr=[[cins[i][0]], [cins[i][1]]], linewidth = 3, color='black')
#plt.legend(['INH-CON', 'INH-TARG', 'NINH-CON', 'NINH-TARG'])
if len(vals) == 2:
	plt.xticks(np.array(b) + bw/2, [lresp + '\nNO LIGHT', lresp + '\nLIGHT'], fontsize=fs_ticks)
	# LINE 1 - CON/TARGET LISTS
	#title = 'COFIRING CORRELATIONS:\nBEFORE VS AFTER DETECTION'
	# LINE 1 - COUPLES FROM JOINT LIST (CON/TARG)
	title = 'COFIRING CORRELATIONS:\nBEFORE VS AFTER DETECTION, joint C-T list'
	title = split2lines(title)
	plt.xlim([-0.3, 1.6])
	
elif len(vals) == 4:
	# LINE 1 - standard B-A C-T correlations

	#plt.xticks(np.array(b) + bw/2, ['INH-CON', 'INH-TARG', 'NINH-CON', 'NINH-TARG'], fontsize=fs_ticks)
	# for thesis
	plt.xticks([0.7, 2.7], ['DISRUPTED HSE', 'CONTROL HSE'], fontsize=fs_ticks)
	plt.xlim([-0.3, 3.5])	

	plt.ylabel('Partial co-firing correlation (r)', fontsize = fs_ticks)

	title = 'COFIRING CORRELATIONS: BEFORE VS AFTER DETECTION (TOP-20% FOR INH) ' + lresp
	#plt.subplots_adjust(top=5.85)

	ysh = 0.01
	print 'WARINING: PRE-SET SIGNIFICANCE LABELS'
	plot_sig(b[1]+bw/2, b[2]+bw/2-0.05, max(vals[1], vals[2])+0.06, 0.03, '****', 20, ysh)
	plot_sig(b[2]+bw/2+0.05, b[3]+bw/2, max(vals[1], vals[2])+0.06, 0.03, '****', 20, ysh)

	#title = 'COFIRING CORRELATIONS: BEFORE VS AFTER DETECTIO, ALL INH EVENTS, ' + lresp +' CELLS'
	#title = 'PARTIAL COF. CORR.: BEFORE VS AFTER DETECTION\n (TOP-20% FOR INH), COND ON LEARN END, ' + lresp + ' CELLS'
	#title = 'PARTIAL COF. CORR.: BEFORE VS AFTER DETECTION (TOP-20% FOR INH), COND ON PRESLEEP - AFTER DETECT, ' + lresp + ' CELLS'

	# LINE 9 - OPTION combined lists of control / target; OR lists of all couples from combined list - before and after ...
	#plt.xticks(np.array(b) + bw/2, ['BEFORE\n NO LIGHT', 'BEFORE\nLIGHT', 'AFTER \nNO LIGHT', 'AFTER\nLIGHT'])
	#title = 'REACTIVATION OF LEARNING END, ' + lresp

	title = split2lines(title)

	plt.subplots_adjust(left=0.16)
else: # 8 bars
	# LINE 5 - with LEND, separately control / target cells before / after ...
	#plt.xticks(np.array(b) + bw/2, ['INH-CON-B', 'INH-CON-A', 'INH-TARG-B', 'INH-TARG-A','NINH-CON-B', 'NINH-CON-A', 'NINH-TARG-B', 'NINH-TARG-A'])
	plt.xticks([2.5, 7.5], ['DISRUPTED HSE', 'CONTROL HSE'], fontsize = fs_ticks)
	plt.xlim(0, 10)
	plt.ylabel('Co-firing correlation (r)', fontsize = fs_ticks)

	# joined lists, but with co-fir corrs with opposite environment during the end-of-learning added - line 9/11 together
	#plt.xticks(np.array(b) + bw/2, ['BEFORE\n NO LIGHT', 'BEFORE\n NO LIGHT/OPP', 'BEFORE\nLIGHT', 'BEFORE\nLIGHT/OPP', 'AFTER\nNO LIGHT', 'AFTER\nNO LIGHT/OPP', 'AFTER\nLIGHT', 'AFTER\nLIGHT/OPP'])
	#title = 'REACTIVATION OF LEARNING END'

	# joined lists - LINE 9 and 11 IF COUPLES FROM combined LIST of CON/TARG are considered 
	#plt.xticks(np.array(b) + bw/2, ['BEFORE\n NO LIGHT', 'BEFORE\n NO LIGHT OPP', 'BEFORE\nLIGHT', 'BEFORE\nLIGHT OPP', 'AFTER \nNO LIGHT', 'AFTER \nNO LIGHT OPP','AFTER\nLIGHT','AFTER\nLIGHT OPP'])
	title = 'REACTIVATION OF LEARNING END ' + lresp

	ysh = 0.01
	plot_sig(b[2]+bw/2, b[3]+bw/2-0.05, max(vals[2], vals[3])+0.03, 0.015, '****', 20, ysh)
	plot_sig(b[4]+bw/2, b[5]+bw/2, max(vals[4], vals[5])+0.03, 0.015, 'n.s.', 20, ysh)

	plt.ylim([0, max(vals) * 1.2])
	plt.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.07)

#plt.title(title + '\n' + spar)


set_yticks_font(25)

plt.savefig(ld + title + '.png')
plt.show()

for i in range(0,len(vals)):
	for j in range(0, i):
		print 'T-test %d vs %d:' % (i, j), ttest_ind(vals[i], vals[j])
