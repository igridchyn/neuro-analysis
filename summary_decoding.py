#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot as plt
import os
from math import sqrt

def load_dic(path, fl = False):
	dic = {}
	for line in open(path):
		if len(line) < 2:
			continue
		ws = line.split(' ')
		if fl:
			dic[ws[0]] = float(ws[1][:-1])
		else:
			dic[ws[0]] = ws[1][:-1]
	return dic

decoutdir = argv[1]

a1 = 'jc181'
a2 = 'jc182'
a3 = 'jc184'
a4 = 'jc188'

days = [[a1, '1124'],
[a1, '1125'],
[a1, '1127'],
[a1, '1130'],
[a2, '0106'],
[a2, '0107'],
[a2, '0109'],
[a2, '0112'],
[a3, '0226'],
[a3, '0227'],
[a3, '0228'],
[a3, '0301'],
[a3, '0304'],
[a4, '0428'],
[a4, '0429'],
[a4, '0430'],
[a4, '0501'],
[a4, '0502'],
[a4, '0503'],
]

# print days

# error before/after target/non-target
erbeta = []
erafta = []
erbent = []
erafnt = []

fpratebeta = []
fpratebent = []
fprateafta = []
fprateafnt = []

for day in days:
	an = day[0]
	d = day[1]

	dic = load_dic('/hdr/data/processing/%s/%s/about.txt' % (an, d))
	# print dic

	eroutpath = decoutdir + 'decer_%s_%s_9l_LIL.out' % (an, d)
	if not os.path.isfile(eroutpath):
		eroutpath = eroutpath.replace('9l', '10l')

	dic_er_lil = load_dic(eroutpath, True)
	dic_er_pl = load_dic(eroutpath.replace('LIL', 'PL'), True)

	print dic['swap']
	
	if dic['swap'] == '0':
		print 'SWAP'
		tarenv = '1'
		nontarenv = '2'
	else:
		print 'NOSWAP'
		tarenv = '2'
		nontarenv = '1'

	# filter by classification precision
	classp = dic_er_pl['CLASSP']
	if classp < 50:
		print 'Ignore day with bad classification precision: %s, %s' % (an, d)
		continue

	erbeta.append(dic_er_lil['EE' + tarenv])
	erbent.append(dic_er_lil['EE' + nontarenv])
	erafta.append(dic_er_pl['EE' + tarenv])
	erafnt.append(dic_er_pl['EE' + nontarenv])

	fpratebeta.append(dic_er_lil['FP' + tarenv] / dic_er_lil['EOCC' + tarenv])
	fpratebent.append(dic_er_lil['FP' + nontarenv] / dic_er_lil['EOCC' + nontarenv])
	fprateafta.append(dic_er_pl['FP' + tarenv] / dic_er_pl['EOCC' + tarenv])
	fprateafnt.append(dic_er_pl['FP' + nontarenv] / dic_er_pl['EOCC' + nontarenv])

N = len(erbeta)

#mn = min(min(erbeta), min(erbent), min(erafta), min(erafnt))
#mx = max(max(erbeta), max(erbent), max(erafta), max(erafnt))
# error before vs. error after; target / non-target colours
#plt.scatter(erbent, erafnt)
#plt.scatter(erbeta, erafta, color = 'r')


# icnrease in target vs. increase in non-target
incta = [erafta[i] / erbeta[i] for i in range(N)]
incnt = [erafnt[i] / erbent[i] for i in range(N)]
mn = min(min(incta), min(incnt))
mx = max(max(incta), max(incnt))
plt.scatter(incta, incnt)
print 'Mean increase target / non-target: %.3f / %.3f' % (np.mean(incta), np.mean(incnt))
print 'STD/sqrt(n) : %.3f / %.3f' % (np.std(incta), np.std(incnt))
print 'Number of days: %d' % N
plt.plot([mn, mx], [mn, mx])
plt.show()


# error ratio before / after
errabe = [erbeta[i] / erbent[i] for i in range(N)]
erraaf = [erafta[i] / erafnt[i] for i in range(N)]
mn = min(min(errabe), min(erraaf))
mx = max(max(errabe), max(erraaf))
plt.scatter(errabe, erraaf)
print 'Mean error ratio before / after: %.2f / %.2f' % (np.mean(errabe), np.mean(erraaf))
plt.plot([mn, mx], [mn, mx])
plt.show()


# fp ratio before / after
fprabe = []
fpraaf = []
for i in range(N):
	if fpratebent[i] > 0 and fprateafnt[i] > 0:
		fprabe.append(fpratebeta[i] / fpratebent[i]) 
		fpraaf.append(fprateafta[i] / fprateafnt[i])

mn = min(min(fprabe), min(fpraaf))
mx = max(max(fprabe), max(fpraaf))
plt.scatter(fprabe, fpraaf)
print 'Mean fp rate ratio before / after: %.2f / %.2f' % (np.mean(fprabe), np.mean(fpraaf))
plt.plot([mn, mx], [mn, mx])
plt.show()


# increase in fprate in trarget vs. non-target : multiplicative and additive
fprainta = []
fprainnt = []
for i in range(N):
	if fpratebent[i] > 0 and fpratebeta[i] > 0:
		fprainta.append(fprateafta[i] / fpratebeta[i]) 
		fprainnt.append(fprateafnt[i] / fpratebent[i])

mn = min(min(fprainta), min(fprainta))
mx = max(max(fprainnt), max(fprainnt))
plt.scatter(fprainta, fprainnt)
print 'Increase (multiplicative) in fp rate in target / non-target: %.2f / %.2f' % (np.mean(fprainta), np.mean(fprainnt))
plt.plot([mn, mx], [mn, mx])
plt.show()
