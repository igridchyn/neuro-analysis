#!/usr/bin/env python2

from sys import argv

def params_map(f):
	pmap = {}
	for line in f:
		if '=' not in line or len(line) < 2:
			continue
		
		ws = line.split('=')
		pmap[ws[0].strip()] = ws[1].strip()

	return pmap

if len(argv) < 3:
	print 'USAGE: (1)<config 1 path> (2)<config 2 path>'
	print 'Compare parameters in the 2 configs, print difference'
	exit(0)

f1 = open(argv[1])
f2 = open(argv[2])

pmap1 = params_map(f1)
pmap2 = params_map(f2)

for key in pmap1:
	if key not in pmap2:
		print key, ' not in 2nd file'
	elif pmap1[key] != pmap2[key]:
		print 'different values of %s : %s / %s' % (key, pmap1[key], pmap2[key])

for key in pmap2:
	if key not in pmap1:
		print key, 'no in 1st file'
