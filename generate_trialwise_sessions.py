#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *
from tracking_processing import *
import pyperclip

#============================================================================
def read_trials(path):
        trials = []
        for line in open(path):
                if len(line) < 3:
                        continue
                trials.append([int(w) for w in line.split(' ')])
        return trials
#============================================================================
def trial_environments(whl, trials):
        envs = []
        for t in trials:
                # find first valid (> EPS) position in the whl and see where it lies
                i = t[0] / 480 + 1
                iend = t[1] / 480 + 1
                while i < iend and whl[i][0] < EPS:
                        i += 1
                envs.append(int(whl[i][0] > 200))
        return envs
#============================================================================
def print_arrays():
        print '\n\n\n'
        text = 'pf.sessions\n' + str(len(pfsessions)) + ' ' + ' '.join([str(t) for t in pfsessions]) + '\npf.groups\n' + str(len(pfgroups)) + ' ' + ' '.join([str(t) for t in pfgroups]) + '\n\n'
        print text
        pyperclip.copy(text)
        # print '(copied to clipboard)'
#============================================================================

# create sessions list for LFPO config that has the 
if len(argv) > 1:
	print 'NEEDS TO RUN IN THE DAY DIRECTORY, NO PARAMETERS REQUIRED'

EPS = 0.01

params = ['%{animal}', '%{day}', '%{FULL}']
params = resolve_vars(params)
[animal, day, full] = params

tpath_f  =  '9f/%s_%s_9f.whl.trials'  % (animal, day)
tpath_l  =  '9l/%s_%s_9l.whl.trials'  % (animal, day)

whlpath_f  =  '9f%s/%s_%s_9f.whl.scaled'  % (full, animal, day)
whlpath_l  =  '9l%s/%s_%s_9l.whl.scaled'  % (full, animal, day)

sspath_f  =  '9f%s/session_shifts.txt' % full
sspath_l  =  '9l%s/session_shifts.txt' % full

trials_l = read_trials(tpath_l)
whl_l =  whl_to_pos(open(whlpath_l), False)
# envs for 9f are always 0-1 if it exists
envs_l = trial_environments(whl_l, trials_l)

# DEBUG
#print trials_l
#print envs_l

pfsessions = []
pfgroups = []

# should be true for all except 1123 ?
if os.path.isfile(sspath_f):
        HAVEF = True
        sessions_f =  read_int_list(sspath_f)
        whl_f = whl_to_pos(open(whlpath_f), False)
else:
        HAVEF = False
sessions_l =  read_int_list(sspath_l)

# DEBUG
#print 'HAVEF = ', HAVEF

oness = sessions_f[1] if HAVEF else 0

if day == '1123':
	# find first trial in env 0 and 1
	# 1123 9l is 11+11+10+10
	pfsessions.append(trials_l[0][1]) # end of 2      E1 trial in 9L
        pfgroups.append(1) # the first interval - from 0 to frist entry is 1 = 1st trial
        pfsessions.append(trials_l[10][0]) # start of 1st E2 trial in 9L
        pfgroups.append(0)
        pfsessions.append(trials_l[10][1]) # end of 2nd        E2 trial in 9L
        pfgroups.append(1)

	# 6th trial in every environment
	pfsessions.append(trials_l[5][0])
	pfgroups.append(0)
	pfsessions.append(trials_l[5][1])
	pfgroups.append(2)
	pfsessions.append(trials_l[16][0])
	pfgroups.append(0)
	pfsessions.append(trials_l[16][1])
	pfgroups.append(2)
	
	# now beginnign and end of the 10th trial (or last trial?) - use last here 
	pfsessions.append(trials_l[30][0])
	pfgroups.append(0)
	pfsessions.append(trials_l[30][1])	
	pfgroups.append(3)
	pfsessions.append(trials_l[40][0])
	pfgroups.append(0)
	pfsessions.append(trials_l[40][1])
	pfgroups.append(3)
	pfgroups.append(0)

	print_arrays()
	exit(0)
	
# first trial in every environment is in 9f - except for 
pfsessions.append(oness)
pfgroups.append(1)

# find 6th trial in every environment - or 5th in 9l
t6_0 = 0
t6_1 = 0

t_cnt = 0
i = 0
while i < len(envs_l) and t_cnt < 5:
	if envs_l[i] == 0:
		t_cnt += 1
	i += 1
t6_0 = i-1
t_cnt = 0
i = 0
while i < len(envs_l) and t_cnt < 5:
	if envs_l[i] == 1:
		t_cnt += 1
	i += 1
t6_1 = i-1

print '5th trial in learning for envs 0/1 are:', t6_0, t6_1 

# order doesnt matter just swap if need so that t6_0 is earlier
if t6_0 > t6_1:
	tmp = t6_1
	t6_1 = t6_0
	t6_0 = tmp

pfsessions.append(oness + trials_l[t6_0][0])
pfgroups.append(0)
pfsessions.append(oness + trials_l[t6_0][1])
pfgroups.append(2)
pfsessions.append(oness + trials_l[t6_1][0])
pfgroups.append(0)
pfsessions.append(oness + trials_l[t6_1][1])
pfgroups.append(2)

# find last trial in envery environment
# obviously, very last recorded trial is last in corresponding environment; trace back to find last in the other environment
elast = envs_l[-1]
i = -2
while envs_l[i] == elast:
	i -= 1
elast_other = i
pfsessions.append(oness + trials_l[elast_other][0])
pfgroups.append(0)
pfsessions.append(oness + trials_l[elast_other][1])
pfgroups.append(2)
pfsessions.append(oness + trials_l[-1][0])
pfgroups.append(0)
pfsessions.append(oness + trials_l[-1][1])
pfgroups.append(2)
pfgroups.append(0)

print_arrays()
