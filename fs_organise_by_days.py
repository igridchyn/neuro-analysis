from sys import argv
ifrom sets import Set
import re
import os
import shutil

def split_any(string, symbols):
	s2 = Set([string])
	for sy in symbols:
		s1 = Set([])
		for s in s2:
			s1 = s1.union(Set(s.split(sy)))
		s2 = s1

	return s2

if len(argv) < 2:
	print 'Split recording files with different dates in the same directory into day-wise directories.'
	print 'Usage: ' + argv[1] + ' <dir with bin files> <animal id>'

dr = argv[1]
animal = argv[2]

if not dr.endswith('/'):
	dr = dr + '/'

days = Set([])

for file in os.listdir(dr):
	if file.startswith(animal):
		# print file
		parts = file.split('_')
		if len(parts) > 1 and len(parts[1]) < 5:
			days.add(parts[1])

print days

for day in days:
	if not os.path.exists(dr + day):
		os.makedirs(dr + day)

	for file in os.listdir(dr):
		if file.startswith(animal + '_' + day):
			shutil.move(dr + file, dr + day + '/' + file)
			print 'move: ', dr + file, dr + day + '/' + file
