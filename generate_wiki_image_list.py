#!/usr/bin/env python3
from sys import argv
import os

if len(argv) < 4:
    print('USAGE: (1)<line> (2)<image number placeholder> (3)<starting number> (4)<ending number (indluding)> (5)<integer format> or\n(1)<line> (2)<filename placeholder> (3)<directory with image array>')
    exit(0)

line = argv[1]
subst = argv[2]

if len(argv) < 5:
    dirpath = argv[3]
    for fname in os.listdir(dirpath):
        if os.path.isfile(os.path.join(dirpath,fname)):
            print line.replace(subst, fname)
    exit(0)

nstart = int(argv[3])
nend = int(argv[4])
iform = argv[5]

for n in range(nstart, nend+1):
    print(line.replace(subst, iform % n))
