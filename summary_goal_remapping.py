#!/usr/bin/env python2

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *
from scipy.stats import ttest_rel, ttest_ind, wilcoxon, mannwhitneyu, kstest, ks_2samp
import statsmodels
from scipy import stats

def plot_kde(x, y):
	xmin = x.min()
	xmax = x.max()
	ymin = y.min()
	ymax = y.max()
	X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
	positions = np.vstack([X.ravel(), Y.ravel()])
	kernel = stats.gaussian_kde(np.vstack([x, y]))
	Z = np.reshape(kernel(positions).T, X.shape)
	print Z.shape
	plt.imshow(np.rot90(Z), extent=[xmin, xmax, ymin, ymax])
	plt.scatter(x, y, s = 0.2)


if len(argv) < 11:
	print 'USAGE: (1)<file name> (2)<minrate> (3)<maxrate> (4)<response> (5)<response file> (6)<maxpfs> (7)<limit on the distance to goal in the 1st session> (8)<min selectivity> (9)<limit on distance from SB peak> (10)<file-list of directories>'
	exit(0)

suppress_warnings()

ld = log_call(argv)

grout_path = argv[1]
MINR = float(argv[2])
MAXR = float(argv[3])
sresp = argv[4]
resp_path_gen = argv[5]
MAXPFS = float(argv[6])
DLIM = float(argv[7])
MINSEL = float(argv[8])
SBD_MIN = float(argv[9])
SHOW = True

dpos = grout_path.find('.')
#fignamesuf = '/home/igor/resim/_AUTOSAVE/GD_' + grout_path[10:dpos] + '_' + argv[2] + '_' + argv[3] + '_' + argv[6] + '_' + argv[8] + '_' + argv[9] + '_'
fignamesuf = '/home/igor/Pictures/19-10-28/GD/GD_' + grout_path[10:dpos] + '_' + argv[2] + '_' + argv[3] + '_' + argv[6] + '_' + argv[8] + '_' + argv[9] + '_'

dlist_path = argv[-1]

gr_out_c = []
gr_out_t = []

pss = 0
tot = 0

# load goal remap output + resposne + coh / spars
for dline in open(dlist_path):
	if len(dline) < 2:
		continue

	wd = os.getcwd()
	os.chdir(dline[:-1])
	resp_path = resolve_vars([resp_path_gen])[0]
	os.chdir(wd)

	gr_day = []

	log_file(ld, dline[:-1] + '/' + grout_path, False)

	for line in open(dline[:-1] + '/' + grout_path):
		gr_day.append(line_to_floats(line))
	gr_day = np.array(gr_day)

	# def cell_filter_rates(dr, rates, mincoh, maxspars, sresp, respfile, sel, minpfr, maxpfr, pfspath(1-2), maxpfs)	
	#ind_c, ind_t = cell_filter_rates(dline[:-1], gr_day, 0.5, 0.3, sresp, resp_path, MINSEL, MINR, MAXR, 'PFS_1_2_FTS_1.out', MAXPFS, 'PFS_2_4_FTS_1_OCC-5_MEAN.out')
	#ind_c, ind_t = cell_filter_rates(dline[:-1], gr_day, 0.5, 0.3, sresp, resp_path, MINSEL, MINR, MAXR, 'PFS_1_2_FTS_1_OCC-5_MEANS.out', MAXPFS, 'PFS_2_4_FTS_1_OCC-5_MEAN.out')
	ind_c, ind_t = cell_filter_rates(dline[:-1], gr_day, 0.5, 0.3, sresp, resp_path, MINSEL, MINR, MAXR, 'PFS_1_2_FTS_1_OCC-5_MEANS.out', MAXPFS, 'PFS_2_3_FTS_1_OCC-5_MEAN.out')

	if len(gr_out_c) > 0:
		gr_out_c = np.concatenate((gr_out_c, gr_day[ind_c,:]))
		gr_out_t = np.concatenate((gr_out_t, gr_day[ind_t,:]))
	else:
		gr_out_c = gr_day[ind_c, :]
		gr_out_t = gr_day[ind_t, :]

	pss += np.sum(ind_c) + np.sum(ind_t)
	tot += 2 * len(ind_c)

log_and_print(ld, 'Passing criteria (mean con/targ) : %d out of %d' % (pss, tot))

# gr_out = np.array(gr_out)

ind_c = gr_out_c[:,4] < DLIM
ind_t = gr_out_t[:,5] < DLIM

if gr_out_c.shape[1] > 18:
	print 'FILTER BY DISTANCE FROM THE SB'
	ind_c = ind_c & (gr_out_c[:,18] > SBD_MIN)
	ind_t = ind_t & (gr_out_t[:,19] > SBD_MIN)

log_and_print(ld, 'Passing cells C/T %d/%d' % (np.sum(ind_c), np.sum(ind_t)))

gd_cb = gr_out_c[ind_c,4]
gd_ca = gr_out_c[ind_c,6]
gd_tb = gr_out_t[ind_t,5]
gd_ta = gr_out_t[ind_t,7]

#if gr_out_c.shape[1] > 16:
#	print 'WARNING !!!!!!!!! : divide distance from peak to the goal by distance from SB to the goal'
#	gd_cb /= gr_out_c[ind_c,16]
#	gd_ca /= gr_out_c[ind_c,16]
#	gd_tb /= gr_out_t[ind_t,17]
#	gd_ta /= gr_out_t[ind_t,17]
#
#else:
#	print 'WARNING: Old format, no distance from SB to G information'

if gr_out_c.shape[1] > 8 and False:
	# just distance between peaks before and after
	pd_c = np.sqrt((gr_out_c[ind_c, 8] - gr_out_c[ind_c, 10]) ** 2 + (gr_out_c[ind_c, 9] - gr_out_c[ind_c, 11]) ** 2)
	pd_t = np.sqrt((gr_out_t[ind_t, 12] - gr_out_t[ind_t, 14]) ** 2 + (gr_out_t[ind_t, 13] - gr_out_t[ind_t, 15]) ** 2)
	p_pd = mannwhitneyu(pd_c, pd_t)
	print 'Peak distances, control / target: %.3f / %.3f;	p-value: %.3f' % (np.mean(pd_c), np.mean(pd_t), p_pd[1])

	# pairwise distances: before and after for control and target ...
	pwd_c = []
	for i in range(gr_out_c.shape[0]):
		for j in range(i):
			if not ind_c[i] or not ind_c[j]:
				continue

			dbef =  np.sqrt((gr_out_c[i, 8] - gr_out_c[j, 8]) ** 2 + (gr_out_c[i, 9] - gr_out_c[j, 9]) ** 2)
			daft =  np.sqrt((gr_out_c[i, 10] - gr_out_c[j, 10]) ** 2 + (gr_out_c[i, 11] - gr_out_c[j, 11]) ** 2)
			pwd_c.append([dbef, daft])
	pwd_t = []
	for i in range(gr_out_t.shape[0]):
		for j in range(i):
			if not ind_t[i] or not ind_t[j]:
				continue

			dbef =  np.sqrt((gr_out_t[i, 12] - gr_out_t[j, 12]) ** 2 + (gr_out_t[i, 13] - gr_out_t[j, 13]) ** 2)
			daft =  np.sqrt((gr_out_t[i, 14] - gr_out_t[j, 14]) ** 2 + (gr_out_t[i, 15] - gr_out_t[j, 15]) ** 2)
			pwd_t.append([dbef, daft])

	pwd_c = np.array(pwd_c)
	pwd_t = np.array(pwd_t)
	print pwd_c.shape
	plt.figure()
	plot_kde(pwd_c[:,0], pwd_c[:,1])
	plt.title('Pairwise distances - CONTROL')
	plt.xlabel('BEFORE')
	plt.ylabel('AFTER')
	plt.figure()
	plot_kde(pwd_t[:,0], pwd_t[:,1])
	plt.title('Pairwise distances - TARGET')
	plt.xlabel('BEFORE')
	plt.ylabel('AFTER')
else:
	print 'WARNING !!! IGNORE pairwise statistics'
	#print 'WARNING: old goal file format, ignore distance btween peaks and pairwise distances'


log_and_print(ld, 'BEFORE CON TARG: %.2f / %.2f' % (np.mean(gd_cb), np.mean(gd_tb)))
log_and_print(ld, 'AFTER  CON TARG: %.2f / %.2f' % (np.mean(gd_ca), np.mean(gd_ta)))

#p_bef = ttest_ind(gd_cb, gd_tb)
#p_aft = ttest_ind(gd_ca, gd_ta)
p_bef = mannwhitneyu(gd_cb, gd_tb)
p_aft = mannwhitneyu(gd_ca, gd_ta)

diffs_con = gd_ca - gd_cb
diffs_targ = gd_ta - gd_tb
p_diff = mannwhitneyu(diffs_con, diffs_targ)[1]
u_diff = mannwhitneyu(diffs_con, diffs_targ)[0]
log_and_print(ld, 'MW U-test difference: %.5f / U = %.5f' % (p_diff, u_diff))
ss_p_diff = p_to_sig_str(p_diff)

# normalized differences
norm_diffs_con = (gd_ca - gd_cb) / (gd_ca + gd_cb)
norm_diffs_targ = (gd_ta - gd_tb) / (gd_ta + gd_tb)
p_norm_diff = mannwhitneyu(norm_diffs_con, norm_diffs_targ)[1]
u_norm_diff = mannwhitneyu(norm_diffs_con, norm_diffs_targ)[0]
log_and_print(ld, 'MW U-test normalized difference: %.5f / U = %.5f' % (p_norm_diff, u_norm_diff))
ss_p_norm_diff = p_to_sig_str(p_norm_diff)

log_and_print(ld, 'MW U-test p-value before : %.5f / U = %.5f' % (p_bef[1], p_bef[0]))
log_and_print(ld, 'MW U-test p-value after: %.5f / U = %.5f' % (p_aft[1], p_aft[0]))

ecdf_con =  statsmodels.distributions.ECDF(gd_ca)
ecdf_targ = statsmodels.distributions.ECDF(gd_ta)
ecdf_diff_con =  statsmodels.distributions.ECDF(diffs_con)
ecdf_diff_targ = statsmodels.distributions.ECDF(diffs_targ)

# histogram of goal distances - DEBUG
if False:
	plt.figure()
	bx = np.arange(-100, 100, 10)
	hc = np.histogram(diffs_con, bx)
	ht = np.histogram(diffs_targ, bx)
	plt.plot(hc[1][1:], hc[0])
	plt.plot(hc[1][1:], ht[0], color='red')
	#plt.hist(diffs_con, bx, alpha=0.5, width=3)
	#plt.figure()
	#plt.hist(diffs_targ, bx+5, color='red', alpha=0.5, width=3)

ecdf_norm_diff_con =  statsmodels.distributions.ECDF(-norm_diffs_con)
ecdf_norm_diff_targ = statsmodels.distributions.ECDF(-norm_diffs_targ)


ss_ttest_diff = p_to_sig_str(ttest_ind(diffs_con, diffs_targ)[1])
ks_diff = ks_2samp(diffs_con, diffs_targ)
print 'KS DIFFS:', ks_diff
ks_norm_diff = ks_2samp(norm_diffs_con, norm_diffs_targ)
print 'KS NORM_DIFFS:', ks_norm_diff
ss_ks_diff = p_to_sig_str(ks_diff[1])
ss_ks_norm_diff = p_to_sig_str(ks_norm_diff[1])

# append output
fout = open('GD_SUM.out', 'a')
# PARAMETERS - 
# write: 1) ratio of dist before to dist after - control; 2) ratio of target after to control after; 3) significance: before and after
ss_bef = p_to_sig_str(p_bef[1])
ss_aft = p_to_sig_str(p_aft[1])
#fout.write('%70s pb=%5s pa=%5s rba=%.2f rtc=%.2f rnd=%.2f\n' % (' '.join(argv[2:5] + argv[6:9]), ss_bef, ss_aft, np.mean(gd_ca)/np.mean(gd_cb), np.mean(gd_ta)/np.mean(gd_ca), np.mean(norm_diffs_targ)/np.mean(norm_diffs_con)))
fout.write('%70s pb=%5s pa=%5s pdi=%5s pksdi=%5s pndi=%5s pksndi=%5s\n' % (' '.join(argv[2:5] + argv[6:10]), ss_bef, ss_aft, ss_p_diff, ss_ks_diff, ss_p_norm_diff, ss_ks_norm_diff))
# to visually separate blocks during brute-forcing
if ';' not in sresp and float(sresp) > 0.4:
	fout.write('\n')
fout.close()
#exit(0)

bx = [0,1,2,3]
mar = np.array( [np.mean(gd_cb), np.mean(gd_tb),np.mean(gd_ca), np.mean(gd_ta)])
# ns = np.array([len(gr_out_c[:,i]) for i in range(4,8)])
ns = np.array([len(gd_cb), len(gd_tb), len(gd_ca), len(gd_ta)])

# DEBUG - scatters of goal distances, before vs. after
if False:
	plt.figure()
	plt.scatter(gd_cb, gd_ca)
	plt.scatter(gd_tb, gd_ta, color='red')
	plt.xlabel('GD - START OF LEARNING', fontsize=30)
	#plt.ylabel('GD - START OF POST-LEARNING', fontsize=30)
	plt.ylabel('GD - POST-PROBE')
	plt.legend(['Control', 'Target'])
	plt.plot([0, 150], [0, 150], color='black')
	if SHOW:
		plt.show()

plt.figure(figsize=(9,10))
#plt.bar(bx, [np.mean(gd_cb), np.mean(gd_tb),np.mean(gd_ca), np.mean(gd_ta)], color=['b','r','b','r'])
plt.bar([0, 2], [np.mean(gd_cb), np.mean(gd_ca)], color='b')
plt.bar([1,3], [np.mean(gd_tb),np.mean(gd_ta)], color='r')
plt.legend(['Control', 'Target'], fontsize=25)
plt.errorbar([b for b in bx], [np.mean(gd_cb), np.mean(gd_tb),np.mean(gd_ca), np.mean(gd_ta)], yerr=np.array([np.std(gd_cb), np.std(gd_tb),np.std(gd_ca), np.std(gd_ta)]) / np.sqrt(ns), fmt='.', color='black', linewidth = 4)

# DEBUG
#plt.title('Goal distances\n' + ' '.join(argv[1:5]) + '\n' + ' '.join(argv[5:-1]))
# plt.title('DISTANCE FROM PLACE FIELD PEAK\nTO THE GOAL LOCATION')
rapp = 'ALL' if sresp=='0' else ('INHIBITED' if sresp[0] == '-' else ('UNAFFECTED' if ';' in sresp else 'DISINHIBITED'))
fignamesuf += rapp + '_'

#plt.xticks([b+0.5 for b in bx], ['C-BEF', 'T-BEF', 'C-AFT', 'T-AFT'])
#plt.xticks([1, 3], ['START OF\nLEARNING', 'START OF\nPOST-LEARNING'], fontsize=30)
plt.xticks([1, 3], ['Start of\nlearning', 'Post-probe'], fontsize=30)
set_yticks_font(25)
bw = 0.8
plot_sig(0, 1, max(np.mean(gd_cb), np.mean(gd_tb)) + 6, 2, ss_bef, 30, 1)
plot_sig(2, 3, max(np.mean(gd_ca), np.mean(gd_ta)) + 6, 2, ss_aft, 30, 1)
plt.ylabel('Distance, cm', fontsize=30)
plt.xlim([-0.5, 3.5])
plt.ylim([0, 67])# max(np.mean(gd_cb), np.mean(gd_ca), np.mean(gd_tb), np.mean(gd_ta))+ 10])
plt.savefig(fignamesuf + '4B.png')

fvals = open('GD_VALS.txt', 'a')
fvals.write('%f %f %f %f ' % (np.mean(gd_cb), np.mean(gd_tb), np.mean(gd_ca), np.mean(gd_ta)))

if SHOW:
	plt.show()

# change in distance to goal - relative
plt.figure(figsize=(5,10))
plt.bar([0], [np.mean(-diffs_con)], color = ['b'])
plt.bar([1], [np.mean(-diffs_targ)], color = ['r'])
plt.legend(['Control', 'Target'], fontsize=25)
#plt.bar([0,1], [np.mean(-norm_diffs_con), np.mean(-norm_diffs_targ)], color = ['b', 'r'])
w = 0.4
plt.errorbar([0,1], [np.mean(-diffs_con), np.mean(-diffs_targ)], [np.std(diffs_con)/np.sqrt(len(diffs_con)), np.std(diffs_targ)/np.sqrt(len(diffs_targ))], fmt='.', color='black', linewidth=3)
plot_sig(0, 1, max(np.mean(-diffs_con)+np.std(diffs_con)/np.sqrt(len(diffs_con)), np.mean(-diffs_targ)+np.std(diffs_targ)/np.sqrt(len(diffs_targ))) + 2.5, 2, ss_ttest_diff, 30)
#plt.errorbar([0+w,1+w], [np.mean(-norm_diffs_con), np.mean(-norm_diffs_targ)], [np.std(-norm_diffs_con)/np.sqrt(len(diffs_con)), np.std(-norm_diffs_targ)/np.sqrt(len(diffs_targ))], fmt='.', color='black', linewidth=3)
#plt.title('Change in distance to goal')

# DEBUG
#plt.title('PF peak shift towards the goal\n' + rapp)
#plt.title('Relative change in distance to goal')

plt.xlim(-0.5, 1.5)
#plt.xticks([0+w, 1+w], ['CONTROL', 'TARGET'], fontsize=30)
set_yticks_font(30)
plt.ylim([0, max(np.mean(-diffs_con)+np.std(diffs_con)/np.sqrt(len(diffs_con)), np.mean(-diffs_targ)+np.std(diffs_targ)/np.sqrt(len(diffs_targ))) + 10])
plt.xticks([],[])
plt.ylabel('Distance, cm', fontsize=30)
plt.subplots_adjust(left=0.22, right=0.98, bottom=0.02, top=0.99)
plt.savefig(fignamesuf + '2B.png')
if SHOW:
	plt.show()

fvals.write('%f %f\n' % (np.mean(-diffs_con), np.mean(-diffs_targ)))

plt.figure(figsize=(10,9))
lw = 4
#plt.plot(ecdf_con.x, ecdf_con.y, linewidth = lw)
#plt.plot(ecdf_targ.x, ecdf_targ.y, color = 'red', linewidth = lw)
#plt.plot(ecdf_diff_con.x,  ecdf_diff_con.y, linewidth = lw)
#plt.plot(ecdf_diff_targ.x, ecdf_diff_targ.y, color = 'red', linewidth = lw)
plt.plot(ecdf_norm_diff_con.x,  ecdf_norm_diff_con.y, linewidth = lw)
plt.plot(ecdf_norm_diff_targ.x, ecdf_norm_diff_targ.y, color = 'red', linewidth = lw)

plt.grid()
# plt.xlabel('Distance to goal')
fs = 30
plt.xlabel('Relative change in distance to goal', fontsize=fs)
#plt.ylabel('Cumulative %', fontsize=fs)
plt.ylabel('Proportion', fontsize=fs)
plt.legend(['Control', 'Target'], fontsize = 25, loc = 'best')

set_xticks_font(25)
set_yticks_font(25)

plt.axvline(x = 0, color = 'black')

#plt.title('Rates %.1f-%.1f, Resp %s, PFS<%.2f' % (MINR, MAXR, sresp, MAXPFS))
#plt.title('Difference in the distance to the goal\n' + ' '.join(argv[1:5]) + '\n' + ' '.join(argv[5:-1]))
# plt.title('Relative shift towards the goal\n' + ' '.join(argv[1:5]) + '\n' + ' '.join(argv[5:-1]))

#plt.savefig(ld + 'ECDF_GOALDISTS.png')
plt.savefig(fignamesuf + 'ECDF.svg')
if SHOW:
	plt.show()
