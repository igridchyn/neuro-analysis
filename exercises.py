#!/usr/bin/env python

import numpy as np
# ====================================================================================================================================================================================
# BUBBLE SORT
a = [1,6,2,1,2,3,5,7,8,9,2,3]
bot = 0
i = 0
while bot < len(a):
    while i < len(a)
#  ... in in GD/LEARN/ML : Exercises.ipynb


# ====================================================================================================================================================================================
# SWAP ARRAY
a = [1,6,2,1,2,3,5,7,8,9,2,3]
for i in range(len(a) // 2):
    tmp = a[i]
    a[i] = a[-(i+1)]
    a[-(i+1)] = tmp
print(a)

# SOLUTION 2
print(list(reversed(a)))

# ====================================================================================================================================================================================
# BINARY SEARCH IN SORTED
a = np.random.randint(0, 1000, 100)
a = sorted(a)
print(a)
low = 0
high = len(a) - 1
targ = 213
while low < high:
    mid = (high+low) // 2
    if a[mid] == targ:
        print('FOUND AT', mid)
        break

    if a[mid] > targ:
        high = mid - 1
    else:
        low = mid + 1
    
# ====================================================================================================================================================================================
# FIND PIVOT IN ROTATED ARRRAY; PIVOT = first element beraking order
rot = np.random.randint(100)
a = a[rot:] + a[:rot]
print('ROTATED AT:', rot)
print(a)
low = 0
high = len(a) - 1
while low < high:
    mid = (high + low) // 2
    if a[mid] > a[0]:
        low = mid + 1
    else:
        high = mid
print('PIVOT AT', low, a[low])
# now for search in pivoted - compare to pivot + search in left or right

# ====================================================================================================================================================================================
# GIVEN ARRAY, MOVE ALL 0s to start while keeping all other sorted
# 2 POINTER TECHNIQUE: if read == 0, continue (keep write there to replace) otherwise, swap read and write (write at 0, read at non-0)
a = np.random.randint(0, 5, 20)
print(a)
read = len(a) - 1
write = len(a) - 1
while read >= 0:
    if a[read] == 0:
        read -= 1
    else:
        a[write] = a[read]
        a[read] = 0
        read -= 1
        write -= 1
print('MOVED 0S', a)
