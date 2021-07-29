#!/usr/bin/env python3

import numpy as np
from sys import argv

d = np.loadtxt(argv[1])
print(max(d))
