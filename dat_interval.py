#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *
import struct
from scipy.signal import butter, lfilter
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

class DialogExample(Gtk.Dialog):

    def __init__(self, parent=None):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
            (Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_YES, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label("ADD EVENT TO LIST ?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

#=====================================================================================================================
if len(argv) < 8:
	print 'USAGE: (1)<dat file> (2)<interval start> (3)<duration before> (4)<duration after> (5)<channel> (6)<output prefix for .out/.sig> (7)<TS shift>'
	exit(0)

path = argv[1]
#offset = int(argv[2])
duration_before = int(argv[3])

if os.path.isfile(argv[4]):
	duration_after = read_int_list(argv[4])
else:
	duration_after = [int(argv[4])]

chan = int(argv[5])
ts_shift = int(argv[7])

f = open(path)

if os.path.isfile(argv[2]):
	offsets = read_int_list(argv[2])
else:
	offsets = [int(argv[2])]

fig = plt.figure(figsize=(18,5))
# not to wait for losing - interactive on
# plt.ion() # + draw for dialog case
ax = plt.gca()

opref = argv[6]
fo = open('%s.out' % opref, 'a')
fos = open('%s.sig' % opref, 'w')

cnt = -1
for offset in offsets:
	cnt += 1
	#
	f.seek(128 * (offset - duration_before - ts_shift) * 2)

	dat = []
	for t in range(duration_before + duration_after[min(len(duration_after)-1, cnt)]):
		f.read(chan * 2)
		dat.append(struct.unpack('h', f.read(2))[0])
		f.read((127 - chan) * 2)

	# RIPPLES
	#dt = butter_bandpass_filter(dat, 150, 250, 24000, order=1)
	# dt = butter_bandpass_filter(dat, 6, 12, 24000, order=1) # 4-12
	dt = butter_bandpass_filter(dat, 6, 10, 24000, order=1) # 4-12

	#if max(dt) < 2000:
	#MINPOW = 2000
	# TEMPORARILY DUMP ALL !
	MINPOW = 0
	if max(dt[(duration_before - 20*24):(duration_before + 24*100)]) < MINPOW:
		print 'SKIP %d' % offset
		continue
		#exit(0)

	NSKIP = 4500
	print 'WARNING: SKIP FRIST %d data points in plotting and writing to file' % NSKIP

	ax.clear()
	plt.title(argv[2])
	plt.plot(dt[NSKIP:])
	plt.axvline(x = duration_before, color='red')
	plt.axvline(x = duration_before + 2400, color='red')
	#plt.ylim([-3600, 3600])
	plt.ylim([-70, 70])
	plt.draw()
	plt.show()

	# write signal to file
	fos.write('%d\n' % (offset))
	for i in range(NSKIP, len(dt)):
		fos.write('%d ' % dt[i])
	fos.write('\n')

	#dialog = DialogExample()
	#response = dialog.run()
	#if response == Gtk.ResponseType.OK:
	print("WRITE TIMESTAMP TO THE FILE")
	fo.write('%d\n' % (offset))
	#elif response == Gtk.ResponseType.CANCEL:
	#    print("SKIP EVENT MANUALLY")
	#dialog.destroy()
	







