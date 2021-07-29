#!/usr/bin/env python3

import time
from sys import argv
import numpy as np
from matplotlib import pyplot
import os
#from iutils import *
#from call_log import *
import struct
from scipy.signal import butter, lfilter

#import gi
#gi.require_version('Gtk', '3.0')
#from gi.repository import Gtk

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

# filter in the 150-250 band

if len(argv) < 5:
	print('USAGE: (1)<dat> (2)<channel> (3)<freq MIN> (4)<freq MAX>')
	exit(0)

dpath = argv[1]
chan = int(argv[2])

FREQMIN = int(argv[3])
FREQMAX = int(argv[4])

f = open(dpath, 'rb')
fo = open(dpath + '.%s.filt.%s-%s' % (argv[2], argv[3], argv[4]), 'wb')

eof = False

# RIPPLE: 150-250
b, a = butter_bandpass(FREQMIN, FREQMAX, 24000, order=1)
# THETA 5 -11
#b, a = butter_bandpass(5, 11, 24000, order=1)
# DELTA 1-4
# b, a = butter_bandpass(1, 4, 24000, order=1)


while not eof:
    start_time = time.time()	

    dat = []
    batch = 1000000
    # ? faster to read big batch and take every chan's point ?
    for t in range(batch):
            neof = f.read(chan * 2)
            if not neof:
                    eof = True
                    batch = t
                    break
            dat.append(struct.unpack('h', f.read(2))[0])
            f.read((127 - chan) * 2)

    #dt = butter_bandpass_filter(dat, 150, 250, 24000, order=1)
    dt = lfilter(b, a, dat)

    print(len(dt))
    # DEBUG
    print(type(dt))
    dti = dt.astype(int)
    fo.write(struct.pack('%dh' % batch, *dti))

    print("--- %s seconds ---" % (time.time() - start_time))
