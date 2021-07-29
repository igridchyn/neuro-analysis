#!/usr/bin/env python2

from sys import argv
from iutils import *
from tracking_processing import *
import os
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

        f = open('sessions_groups.txt', 'w')
        f.write(' '.join([str(t) for t in pfsessions]) + '\n' + ' '.join([str(t) for t in pfgroups]))
#============================================================================

if len(argv) > 1:
	print 'NEEDS TO RUN IN THE DAY DIRECTORY, NO PARAMETERS REQUIRED'

EPS = 0.01
params = ['%{animal}', '%{day}', '%{FULL}']
params = resolve_vars(params)
[animal, day, full] = params

# configuration 1 
#	I1: 2 first trials of  L-1 - all in 9f + 1st trial and 6th trials in 9l
# 	I2: 2 last  trials of  L-2 - trials 14-15 and 19-20 in 9l
#	I3: 1 first trial  of  NL-1
#	I4: 2 last  trials of  NL-2

# load L trials
tpath_f  =  '9f/%s_%s_9f.whl.trials'  % (animal, day)
tpath_l  =  '9l/%s_%s_9l.whl.trials'  % (animal, day)
tpath_nl = '16l/%s_%s_16l.whl.trials' % (animal, day)

whlpath_f  =  '9f%s/%s_%s_9f.whl.scaled'  % (full, animal, day)
whlpath_l  =  '9l%s/%s_%s_9l.whl.scaled'  % (full, animal, day)
whlpath_nl = '16l%s/%s_%s_16l.whl.scaled' % (full, animal, day)

sspath_f  =  '9f%s/session_shifts.txt' % full
sspath_l  =  '9l%s/session_shifts.txt' % full
sspath_nl = '16l%s/session_shifts.txt' % full
sspath_post = '14post%s/session_shifts.txt' % full

if os.path.isfile(sspath_f):
	HAVEF = True
	sessions_f =  read_int_list(sspath_f)
	whl_f = whl_to_pos(open(whlpath_f), False)
else:
	HAVEF = False

print 'HAVEF = ', HAVEF

sessions_l =  read_int_list(sspath_l)
sessions_nl = read_int_list(sspath_nl)
sessions_post = read_int_list(sspath_post)
whl_l =  whl_to_pos(open(whlpath_l), False)
whl_nl = whl_to_pos(open(whlpath_nl), False)
trials_l = read_trials(tpath_l)
trials_nl = read_trials(tpath_nl)
envs_l = trial_environments(whl_l, trials_l)
envs_nl = trial_environments(whl_nl, trials_nl)

oness = sessions_f[1] if HAVEF else 0
twoss = oness + sessions_l[-1] + sessions_post[-1]
postss = oness + sessions_l[-1]

print envs_l, envs_nl

# ??? END OF PREVIOUS OR START OF CURRENT ??? - SB, TAKE MORE !!!
pfsessions = []
# to which group belongs interval (pfsessions[i-1]; pfsessions[i])
pfgroups = []
# easier to enter this one manually
if day == '1123':
        # 1123: no F, L: 11+11+10+10; AFTER UDPATES: 10-11-10-10 !!! -> indices have been adjusted
	pfsessions.append(trials_l[1][1]) # end of 2 	  E1 trial in 9L
	pfgroups.append(1)
	pfsessions.append(trials_l[10][0]) # start of 1st E2 trial in 9L
	pfgroups.append(0)
	pfsessions.append(trials_l[11][1]) # end of 2nd        E2 trial in 9L
	pfgroups.append(1)
	# if 2 last trials are to be used
	#pfsessions.append(trials_l[30][0]) # start of 2nd last E1 trial in 9L
	pfsessions.append(trials_l[26][0]) # start of 5th last E1 trial in 9L
	pfgroups.append(0)
	pfsessions.append(trials_l[30][1]) # end of last E1 trial in 9L
	pfgroups.append(2)
	# if 2 last trials are to be used
	# pfsessions.append(trials_l[40][0]) # start of 2nd last E2 trial in 9L
	pfsessions.append(trials_l[36][0]) # start of 5th last E2 trial in 9L
	pfgroups.append(0)
	pfsessions.append(trials_l[40][1]) # end of last trial in E2 / start of first trial in NL/E1 OR post - if used
	pfgroups.append(2)

	# after end of last trial in 9L and start of the post
	pfsessions.append(postss)
	pfgroups.append(0)

	# post
	pfsessions.append(twoss)
	pfgroups.append(3)

	pfsessions.append(twoss + trials_nl[0][1]) # end of first E1 trial in NL
	pfgroups.append(4)
	# trials_n[8] if 2 last to be used
	pfsessions.append(twoss + trials_nl[5][0]) # start of the last 5 E1 trials in NL
	pfgroups.append(0)
	pfsessions.append(twoss + trials_nl[9][1]) # end of last 5 E1 trials in NL
	pfgroups.append(5)
	pfsessions.append(twoss + trials_nl[10][0]) # start of the first E2 trial in NL
	pfgroups.append(0)
	pfsessions.append(twoss + trials_nl[10][1]) # end of first trial in NL/E2
	pfgroups.append(4)
	# trials_n[18] if 2 last trials are to be used
	pfsessions.append(twoss + trials_nl[15][0]) # start if the last 5 trials in NL / E2
	pfgroups.append(0)
	pfsessions.append(twoss + trials_nl[19][1]) # end of last 5 trials in NL / E2
	pfgroups.append(5)
	pfgroups.append(0)
	print_arrays()
	exit(0)

# NOW CONSIDER HAVING SESSION 9F - 1 TRIAL IN EVERY ENVIRONMENT

# now find out which trials should be used for every interval
# find first trial in every environment in 9L
i=0
while envs_l[i] != 0:
	i += 1
print 'First E1 trial in 9L: ', i

if i == 0:
	pfsessions.append(oness + trials_l[0][1]) # end of 2 sessions in E1
	pfgroups.append(1)
else:
	print 'ERROR: first trial in 9L is not in E1'
	exit(1)

i=0 
while envs_l[i] != 1:
	i += 1
print 'First E2 trial in 9L: ', i
pfsessions.append(oness + trials_l[i][0]) # start of 2nd E2 trial in 9L
pfgroups.append(0)
pfsessions.append(oness + trials_l[i][1]) # end of 2nd E2 trial in 9L
pfgroups.append(1)

# now find the last trials in the 9L
NLAST9L = 4 if day == '0428' else 5 # how many last trials are needed, 4 for 0428 !
i = len(envs_l) - 1
while envs_l[i] == 1:
	i -= 1
print 'Last E1 trial in 9L: ', i
for j in range(i - NLAST9L + 1, i):
	if envs_l[j] != 0:
		print 'ERROR: no last consecutive E1 trials in the 9L'
		exit(2)

pfsessions.append(oness + trials_l[i - NLAST9L + 1][0]) # start of pre-last E1 trial in 9L
pfgroups.append(0)
pfsessions.append(oness + trials_l[i][1]) # end of last E1 trial in 9L
pfgroups.append(2)

i = len(envs_l) - 1
while envs_l[i] == 0:
	i -= 1
print 'Last E2 trial in 9L: ', i
for j in range(i - NLAST9L + 1, i):
	if envs_l[j] != 1:
		print 'EROR: no last consecutive E2 trials in the 9L'
		exit(3)

pfsessions.append(oness + trials_l[i- NLAST9L + 1][0]) # start of the pre-last E2 trial in the 9L
pfgroups.append(0)
pfsessions.append(oness + trials_l[i][1]) # end of the last E2 trial in the 9L
pfgroups.append(2)

# before the beginning of the post, next whole post session
pfsessions.append(postss)
pfgroups.append(0)
pfsessions.append(twoss)
pfgroups.append(3)

# special case for 0106: trial order is  [0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]

NFIRST16L=1
print 'WARNING: USE %d trials from POST-LEARNING for the group 4'
if day != '0106':
	# find the fisrt single trial in the 16L
	i=0
	while envs_nl[i] != 0:
		i += 1
	for j in range(i+1, i+NFIRST16L):
		if envs_nl[j] != 0:
			print 'ERROR: no consecutive first E1 trials in 16L'
		
	print 'First E1 trial in 16L: ', i
	pfsessions.append(twoss + trials_nl[i][0]) # start of the first E1 trial in 16L
	pfgroups.append(0)
	pfsessions.append(twoss + trials_nl[i + NFIRST16L - 1][1]) # end of the NFIRST16L-th E1 trial in 16L
	pfgroups.append(4)

	i=0
	while envs_nl[i] != 1:
		i += 1
	for j in range(i+1, i+NFIRST16L):
		if envs_nl[j] != 0:
			print 'ERROR: no consecutive first E1 trials in 16L'
	print 'First E2 trial in 16L: ', i
	pfsessions.append(twoss + trials_nl[i][0]) # start of the first E2 trial in 16L
	pfgroups.append(0)
	pfsessions.append(twoss + trials_nl[i + NFIRST16L - 1][1]) # end of the NFIRST16L-th E2 trial in 16L
	pfgroups.append(4)
else:
	print 'WARNING: SPECIAL CASE TRIALS FOR 0106'
	# [0 1 0 ... 0 1 1 ...]
	pfsessions.append(twoss + trials_nl[0][0]) # start of the first E1 trial in 16L
        pfgroups.append(0)
        pfsessions.append(twoss + trials_nl[NFIRST16L][1]) # end of the NFIRST16L-th E1 trial in 16L
        pfgroups.append(4)
	
	if NFIRST16L > 1:
	        pfsessions.append(twoss + trials_nl[8-NFIRST16L+2][0]) # end of the NFIRST16L-th E1 trial in 16L
	        pfgroups.append(0)
	        pfsessions.append(twoss + trials_nl[8][1]) # end of the NFIRST16L-th E1 trial in 16L
	        pfgroups.append(4)

# how many last trials in 16L to use
NLAST16L = 5
# find last trial in the 16L
i = len(envs_nl) - 1
while envs_nl[i] != 0:
	i -= 1
for j in range(i - NLAST16L + 1, i):
	if envs_nl[j] != 0:
		print 'ERROR: no consecutive last E1 trials in 16L'
		exit(4)
print 'Last E1 trial: ', i+1

pfsessions.append(twoss + trials_nl[i - NLAST16L + 1][0]) # start of the pre-last E1 trial in 16L
pfgroups.append(0)
pfsessions.append(twoss + trials_nl[i][1]) # end of the last e1 trial in 16L
pfgroups.append(5)

i = len(envs_nl) - 1
while envs_nl[i] != 1:
	i -= 1
for j in range(i - NLAST16L + 1, i):
	if envs_nl[j] != 1:
		print 'ERROR: no consecutive last E2 trial in 16L'
		exit(5)

pfsessions.append(twoss + trials_nl[i - NLAST16L + 1][0]) # strat of the pre-last E2 trial in 16L
pfgroups.append(0)
pfsessions.append(twoss + trials_nl[i][1]) # end of the last E2 trial in 16L
pfgroups.append(5)
pfgroups.append(0)

# check if time order is consistent
for i in range(len(pfsessions) - 1):
	if pfsessions[i+1] < pfsessions[i]:
		print 'ERROR: inconsistent temporal order of sessions'
		exit(6)

print_arrays()
