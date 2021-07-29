#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
from sys import argv
import os
from iutils import *
from call_log import log_call
import matplotlib.patches as patches

if len(argv) < 3:
	print 'light_response.py (1)<res_name> (2)<clu_name> (3)<flash_starts> [(4)<res2_name> (5)<clu2_name> (6)<flash_starts2>]'
	exit(0)

# argv = resolve_vars(argv)

# log call
log_call(argv)

def calculate_light_responses(res_name, clu_name, flash_path):
	BIN = 120
	#BIN = 12

	# both to the left and to the right
	NBINS = 30
	# for mean wide
	#NBINS = 80
	
	# regular flashes
	DELAY = 6.15 * 24000
	PULSE_DURATION = 100 * 24
	INTERVAL = 500 * 24
	
	SESSION_DURATION = 10 * 60 * 24000

	# load res and clu
	res = [int(r) for r in open(res_name).read().split('\n') if len(r) > 0]
	clu = [int(r) for r in open(clu_name).read().split('\n') if len(r) > 0]
	
	NCELL = max(clu) + 1
	responses = np.zeros([NCELL, NBINS * 2 + 1])
	
	print len(res), ' spikes ', max(clu), ' cells'
	
	# fill flash starts times
	flash_starts = []
	time = DELAY
	if len(argv) < 4:
		while time < SESSION_DURATION:
			time += INTERVAL + PULSE_DURATION
			flash_starts.append(time)
	else:
		flash_starts = [int(tt.split(' ')[0]) for tt in open(flash_path).read().split('\n') if len(tt) > 0]
	
	# limit pointer
	res_min_ptr = 0
	# current pointer
	res_ptr = 0
	# build histograms
	for flash in flash_starts:
		# new limiting pointer
		while res_min_ptr < len(res) and res[res_min_ptr] < flash - NBINS * BIN:
			res_min_ptr += 1
	
		if res_min_ptr >= len(res):
			break
	
		res_ptr = res_min_ptr
		while res_ptr < len(res) and res[res_ptr] < flash + NBINS * BIN:
			res_bin = (flash - res[res_ptr]) / BIN + NBINS
			responses[clu[res_ptr], res_bin] += 1
			res_ptr += 1
	
	bin_left = [-BIN*(NBINS + 1)*1000/24000 + BIN*1000/24000 * i for i in range(0, NBINS*2 + 1)]
	binw = BIN*1000/24000

	return responses/len(flash_starts) * 24000 / float(BIN), NCELL, bin_left, binw/2

responses1, NCELL, bin_left, binw = calculate_light_responses(argv[1], argv[2], argv[3] if len(argv) > 3 else '')
if len(argv) > 4:
	responses2, NCELL, bin_left, binw = calculate_light_responses(argv[4], argv[5], argv[6] if len(argv) > 5 else '')

bin_left = np.array(bin_left)

if len(argv) > 4:
	binw /= 2

#rpath = argv[1] + '.resp'
#rpath = 'full.05ms.w50.responses'
rpath = 'full.5ms.w100.responses'
#rpath = 'full.5ms.responses'
if os.path.isfile(rpath):
	print 'ERROR: output file exists:', rpath
	exit(1)

f = open(argv[1] + '.respo', 'w')
fe = open(argv[1] + '.respext', 'w')

resdir = os.path.dirname(argv[1]) + 'responses_5ms/'
if not os.path.isdir(resdir):
	os.makedirs(resdir)

responses1 = np.fliplr(responses1)
if len(argv) > 4:
	responses2 = np.fliplr(responses2)

if len(argv) <= 4:
	binw *= 2

rlist= []

np.savetxt(rpath, responses1[1:,:])

#print 'WARNING: early exit'
# exit(0)

for cell in range(1, NCELL):
	# case of regular pulses
	#smbef = np.sum(responses1[cell,22:31])
	#smaft = np.sum(responses1[cell,32:41])
	# responses around SWR - where rate is not affected by sycnhrony
	smbef = np.sum(responses1[cell,11:21])
	smbefall = np.sum(responses1[cell,:21])
	smaft = np.sum(responses1[cell,40:50])

	# write full instead of log ratio of sum
	#for i in range(responses1.shape[1]):
	#	f.write(str(responses1[cell,i) + ' ')
	#f.write('\n')

	if smbef == 0 and smaft == 0:
		response = 0
	elif smbef == 0:
		response = 10
	elif smaft == 0:
		reponse = -10
	else:
	 	response = np.log( smaft/ smbef)
	# case of detected synchrony vs. inhibited synchrony
	if len(argv) > 4:
		# response = sum(responses1[cell,0:14])/sum(responses2[cell,2:16]) / sum(responses1[cell, 26:34]) * sum(responses2[cell, 28:36])
		# 50 ms starting 5 ms after the pulse in both : ratio
		response = sum(responses1[cell, 22:32]) / sum(responses2[cell, 22:32])

	rlist.append(response)

	#fig=plt.figure(figsize=(20,12)) # 20, 12; 10, 6
	fig=plt.figure(figsize=(10,7)) # 20, 12; 10, 6

	#plt.bar(bin_left, responses1[cell, :], binw)
	plt.bar(bin_left[10:], responses1[cell, 10:], binw)

	r1i = patches.Rectangle((0, 0), 100, plt.gca().get_ylim()[1], linewidth=1, facecolor='black', edgecolor='none', alpha=0.25)
        plt.gca().add_patch(r1i)

	set_xticks_font(30)
	set_yticks_font(30)

	#plt.title('Light response of cell %d = %.2f' % (cell, response))
	lfs = 45
	plt.xlabel('Time, ms', fontsize = lfs)
	plt.ylabel('Firing rate, Hz', fontsize = lfs)
	if len(argv) > 4:
		plt.bar(bin_left-binw, responses2[cell, :], binw, color = 'r')
	#plt.show()

	# 0.2 0.15 too much
	# 0.13 0.13  too little
	plt.subplots_adjust(bottom=0.15)
	plt.subplots_adjust(left=0.135)
	plt.grid()

	plt.axvline(x=0, ymin=0, ymax = max(responses1[cell,:]), color='r')
	#plt.savefig(resdir + 'response_' + str(cell) + '_rev4.jpg')
	if smbefall > 10:
		plt.savefig(resdir + 'response_' + str(cell) + '_rev4.png')
	else:
		print 'IGNORE cell %d because of low baseline spiking' % cell
	plt.close(fig)

	# f.write(str(response) + '\n')

	# response + firing rate	
	fe.write('%.2f %.2f\n' % (response, smbefall/21.0))

# write cell responses
# write_list(rlist, argv[3] + '.responses')
