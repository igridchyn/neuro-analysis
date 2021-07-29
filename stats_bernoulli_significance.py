#!/usr/bin/env python

# http://www.stat.wisc.edu/~wardrop/courses/371chapter9b.pdf

from math import sqrt
from scipy.stats import norm
from sys import argv

if len(argv) < 5:
	print 'Usage: (1)<number of successes 1> (2)<number of trials 1> (3)<number of successes 2> (4)<number of trials 2>'
	print 'P-VALUE for 1-sided test comparing 2 bernoilli samples (whether second is larger than the first one'
	exit(0)

X = int(argv[1])
n1 = int(argv[2])
Y = int(argv[3])
n2 = int(argv[4])

p1 = X / float(n1)
p2= Y / float(n2)
p=(X+Y)/float(n1+n2)
pvalue = 1-norm.sf((p1-p2)/sqrt(p*(1-p)*(1/float(n1) + 1/float(n2))))

print 'p-value for 1-sided test: %.2f' % pvalue
