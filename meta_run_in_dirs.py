#!/usr/bin/env python2

from sys import argv
import os
import subprocess
from call_log import log_call

if len(argv) < 4:
	print 'Usage: (1)<script name> (2)<N=number of script parameters> (3)<first script parameter> ... (3+N-1)<N-th script parameter> (3+N)<1st directory> ... (M)<last directory>'
	print 'Run provided script with provided parameters in the provided directories'
	print 'For evaluable expressions use [<expression to be evaluated>] : [] will be replace by `` during call, ^ will be replaced by *'
	exit(0)

log_call(argv)

script = ['python2', '/home/igor/bin/' + argv[1]]
narg = int(argv[2])
args = argv[3:3+narg]

for i in range(len(args)):
	if args[i][0] == '[' and args[i][-1] == ']':
		args[i] = '`' + args[i][1:-1] + '`'
		print 'Evaluatable expression detected at position', i
        args[i] = args[i].replace('^', '*')

args_full = []
for arg in args:
	args_full.append(arg.replace('/', '_FULL/').replace('^', '*'))
	# args_full.append(arg.replace('/9l', '/9l_FULL'))

indir = os.getcwd() + '/'
runarr = script + args
print runarr

runarr_full = script + args_full

full = False

# if file with list of dirs is given:
if len(argv) < narg+3:
	print 'More arguments are required - file with list of directories or argument for every directory'	
	exit(1)

print 'Number of argumenets:', narg
print argv

if os.path.isfile(argv[3+narg]):
	print 'TAKE DIRECTORIES FROM FILE: ', argv[3+narg]
	dlistpath = argv[3+narg]
	del argv[-1]
	for line in open(dlistpath):
		if len(line) > 1:
			argv.append(line[:-1])

for dr in argv[3+narg:]:

	print 'Run %s in directory %s' % (argv[1] , indir + dr)
	os.chdir(indir + dr)

	try:
		if False: # os.path.isdir('16l_FULL') and os.path.isdir('9l_FULL'):
			print subprocess.check_output(runarr_full)
		else:
			if '0106' in dr and '16l' in argv[3] and 'cofiring' in argv[1]:
				argsf = args[:]
				argsf[2] = '%{ss1}'
				argsf[3] = '%{ss3}'
				print 'WARNING: updated 0106 params: ', argsf
				print subprocess.check_output(script + argsf)
			else:
				# print subprocess.check_output(runarr)
				# print ' '.join(runarr)
				process = subprocess.Popen(' '.join(runarr), shell = True)
				rcode = process.wait()
				if rcode > 0:
					print 'ERROR: Subprocess exited with non-0 code: ', rcode
					exit(rcode)
	except subprocess.CalledProcessError as err:
		print 'ERROR OCCURRED: ', err.output
		raise
		exit(7234)
	except:
		print 'ERROR: unknown'
		exit(1123)
