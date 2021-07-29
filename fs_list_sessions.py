#!/usr/bin/env python

from sys import argv
from stat import S_ISREG, ST_CTIME, ST_MODE, ST_MTIME
import os, sys, time

if len(argv) < 2:
	print 'USAGE: (1)<directory with binary recording files named in format JC<id>_<date>_<session>.[bin | BIN] >'
	print 'Output string with session names ordered by binary file modification time'
	exit(0)

dirpath= argv[1]
# path to the directory (relative or absolute)

# get all entries in the directory w/ stats
entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
entries = ((os.stat(path), path) for path in entries)

# leave only regular files, insert creation date
entries = ((stat[ST_MTIME], path)
           for stat, path in entries if S_ISREG(stat[ST_MODE]))
#NOTE: on Windows `ST_CTIME` is a creation date 
#  but on Unix it could be something else
#NOTE: use `ST_MTIME` to sort by a modification date

flist = []
for cdate, path in sorted(entries):
	print time.ctime(cdate), os.path.basename(path)
	flist.append(os.path.basename(path))

slist = ''
for f in flist:
	sesresl = f.split('_')
	if len(sesresl) < 2:
		continue

	sesres = '_'.join(sesresl[2:])

	ws = sesres.split('.')
	if len(ws) < 2:
		continue

	if ws[1] in ['BIN', 'bin']:
		slist += ws[0] + ' '

print slist
