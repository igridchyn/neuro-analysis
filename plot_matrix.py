#!/usr/bin/env python3

import numpy as np
from sys import argv
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from iutils_p3 import *

if len(argv) > 2:
	(fig, axar) = plt.subplots(1, len(argv)-1, figsize=(15,4))
else:
	axar = [plt.gca()]

for i in range(len(argv)-1):
    m = np.loadtxt(argv[i+1])
    pcm = axar[i].imshow(m * 50, interpolation='none', cmap='jet')

    strip_all_axes(axar[i]) 
    axar[i].set_xticks([])
    axar[i].set_yticks([])

    divider = make_axes_locatable(axar[i])
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(pcm, cax=cax)

plt.tight_layout()
#plt.show()
plt.savefig(argv[1] + '.png')
