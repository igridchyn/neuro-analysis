import numpy as np
from matplotlib import pyplot as plt

admeans = []
means2 = np.arange(0, 3, 0.05)

for mean2 in means2:
	N=100000

	v1 = [np.random.normal(0, 1) for i in range(N)]
	v2 = [np.random.normal(1, 1 + mean2) for i in range(N)]

	vad = [abs(v1[i] - v2[i]) for i in range(N)]

	admeans.append(np.mean(vad))

#plt.hist(vad, 100)
plt.plot(means2, admeans)
plt.show()
