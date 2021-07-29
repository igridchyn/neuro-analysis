#!/usr/bin/env python2

import shutil
import os
import glob
from sys import argv

if len(argv) < 3:
	print '(1)<wildcard expression for files to be renamed> (2)<part of filename that is renamed> (3)<string substituted in the filename>'
	exit(0)

print argv

for file in glob.glob(argv[1]):
	if argv[2] not in file:
		continue

	filen = file.replace(argv[2], argv[3])
	shutil.move(file, filen)
	print 'move %s to %s' % (file, filen)
