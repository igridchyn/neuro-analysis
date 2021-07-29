#!/usr/bin/env python

import datetime
import time
import os
import shutil
from sys import argv

def log_call(args):
	#calldir = '/home/igor/Dropbox/IST_Austria/Csicsvari/'
	calldir = '/home/igor/CALL_DUMP/'

	strdt = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
	strdtonly = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
	strdir = os.getcwd()
	cargs = args[:]
	# cargs[0] = cargs[0].split('/')[-1]
	scdir = '/'.join(args[0].split('/')[:-1])
	strargs = ' '.join(cargs)

	# daydir
	daydir = calldir + 'CALL_DUMP/' + strdtonly
	if not os.path.isdir(daydir):
		os.mkdir(daydir)

	# create directory for call dump - git patch plus all images produced
	dumpdir = calldir + 'CALL_DUMP/' + strdtonly + '/'  + strdt
	if os.path.isdir(dumpdir):
		i=1
		while os.path.isdir(dumpdir + '-' + str(i)):
			i+=1
		dumpdir += '-' + str(i) + '/'
	else:
		dumpdir += '/'
	os.mkdir(dumpdir)
	# git patch
	gitcmd = 'cd ' + scdir + '/source; git diff ' + os.path.basename(args[0]) + ' > "' + dumpdir + 'git-diff.patch"; cd -'
	os.system(gitcmd)

	# if meta
	if os.path.isfile(scdir + '/source/' + args[1]):
		gitcmds = 'cd ' + scdir + '/source; git diff ' + args[1] + ' > "' + dumpdir + 'git-diff-argv.patch"; cd -'
		os.system(gitcmds)
	
	fdd = open(dumpdir + 'CALL_INFO.txt', 'w')

	# write to log file
	f = open(calldir + 'CALL_LOG.txt', 'a')

	f.write(strdt + '\n')
	fdd.write(strdt + '\n')
	f.write(strdir + '\n')
	fdd.write(strdir + '\n')
	f.write(strargs + '\n')
	fdd.write(strargs + '\n')

	# input files size and modification date
	for a in args[1:]:
		if os.path.isfile(a):
			f.write(a + '\n')
			fdd.write(a + '\n')
			f.write(time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(os.path.getmtime(a))) + '\n')
			fdd.write(time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(os.path.getmtime(a))) + '\n')
		
	f.write('\n')
	f.close()
	fdd.close()

	# return dump dir for any subsequent operations
	return dumpdir

def log_and_print(logdir, output):
	f = open(logdir + 'out.txt', 'a')
	f.write(output + '\n')
	print output

def log_file(logdir, path, copy=True):
	f = open(logdir + 'out.txt', 'a')
	f.write('LOG FILE: %s, created on: %s\n' % (path, time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(os.path.getmtime(path)))))
	if copy:
		shutil.copy(path, logdir)

#if len(argv) < 1:
#	print 'Usage : <1>(command: ERR / LASTFIG / )'
#	print ' - ERR: mark the last call as flawed by appending ERR- to the name of the dump directory'
#	exit(0)

#if argv[1] == 'ERR':
#	pass
#else:
#	print 'ERROR: unknown command'
