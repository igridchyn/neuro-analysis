#!/usr/bin/env python

from sys import argv
import os
import subprocess

if len(argv) < 3:
	print 'USAGE: (1)<script to run> (2)<file with part of the arguments (which ones specifed in the first line)>'
	exit(0)

script = ['python', '/home/igor/bin/' + argv[1]]
fargs = open(argv[2])
restargs = argv[3:]

# format of the file:
# <total number of arguemnts>
# <M = number of fixed arguments>
# <pos of fixed argument 1> <value of fixed argument 1>
# ...
# <pos of fixed argument M> <value of fixed argument M>
# <list of positions of variable arguments>
# <set of variable arguments 1>
# ...
# <set of variable arguments N>

ntot = int(fargs.readline())
full_args = [''] * ntot
nfix = int(fargs.readline())
for i in range(nfix):
	ws = fargs.readline().split(' ')
        full_args[int(ws[0])] = os.path.expandvars(ws[1][:-1])

# POSITIONS OF VARIABLE ARGUMENTS
lpos = [int(p) for p in fargs.readline().split(' ') if len(p) > 0]

for line in fargs:
	wsargs = line.split(' ')
	wsargs[-1] = wsargs[-1][:-1]
	for i in range(len(lpos)):
		full_args[lpos[i]] = wsargs[i]

	try:
		print subprocess.check_output(script + full_args)
        except subprocess.CalledProcessError as err:
                print 'ERROR OCCURRED: ', err.output
        except:
                print 'ERROR: unknown'

	# print full_args
	
