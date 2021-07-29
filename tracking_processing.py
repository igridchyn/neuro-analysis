import numpy as np
from numpy import sqrt

# ====================================================================================================================================================================
def smooth_whl(whl):
    whls = []
    rad = 5
    for i in range(rad):
        whls.append(whl[i])

    for i in range(rad, len(whl) - rad):
        # don't smooth if from different environments
        e1 = False
        e2 = False
        EBORD = 200
        for j in range(-rad, rad+1):
            if whl[i+j][0] > 0.1 and whl[i+j][0] < EBORD:
                e1 = True
            if whl[i+j][0] > 0.1 and whl[i+j][0] > EBORD:
                e2 = True
        if e1 and e2:
            whls.append(whl[i])
            continue

        x = sum([p[0] for p in whl[i-rad:i+rad+1]])
        y = sum([p[1] for p in whl[i-rad:i+rad+1]])
        whls.append([x / float(2 * rad + 1), y / float(2 * rad + 1)])

    for i in range(len(whl) - rad, len(whl)):
        whls.append(whl[i])

    return whls
# ====================================================================================================================================================================
def path_length(whl):
    l = 0
    EPS = 0.01
    DMAX = 100
    for i in range(len(whl) - 1):
        d = distance(whl[i], whl[i+1])
        if whl[i][0] > EPS and whl[i+1][0] > EPS and d < DMAX:
            l += d
    return l

# ====================================================================================================================================================================
def whl_to_pos(f, fill_gaps):
    pos = []
    for line in f:
        fs = [float(n) for n in line.split(' ') if len(n) > 0]
        if fs[0] < 1000 and fs[2] < 1000:
            pos.append([(fs[0]+fs[2])/2, (fs[1]+fs[3])/2])
        else:
            if fs[0] < 1000:
                pos.append([fs[0], fs[1]])
            else:
                if fs[2] < 1000:
                    pos.append([fs[2], fs[3]])
                else:
                    pos.append([0, 0])

    # filling gaps with previous value - this will not add high-speed entires but will allow for seamless display and easier speed estimation
    if fill_gaps:
        for i in range(1, len(pos)):
            if pos[i][0] == 0:
                pos[i]=pos[i-1][:]

    return pos
# ====================================================================================================================================================================
def whl_to_speed(whl):
    speed = []
    SRAD = 8
    for i in range(0, SRAD):
        speed.append(0)
    for i in range(SRAD, len(whl)-SRAD):
        speed.append(sqrt((whl[i+SRAD][0]-whl[i-SRAD][0])**2 + (whl[i+SRAD][1]-whl[i-SRAD][1])**2))
    for i in range(len(whl)-SRAD, len(whl)):
        speed.append(0)

    # print 'Speed size before smooth: %d' % len(speed)
    # average smoothing
    speed = np.convolve(np.array(speed), np.array([1] * 15) / 15.0, mode='same')
    # print 'Speed size after smooth: %d' % len(speed)

    return speed
# ====================================================================================================================================================================
def distance(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
# ====================================================================================================================================================================
def occupancy_map(pos, bsize, speed_thold = 0):
# ====================================================================================================================================================================
    speed = whl_to_speed(pos)

    mp = np.zeros((max([p[1]/bsize for p in pos if p[1] > 0]) + 1, max([p[0]/bsize for p in pos if p[0] > 0]) + 1))
    for i in range(len(pos)):
        p = pos[i]
        if p[0] > 1000 or p[0] == 0 or speed[i] < speed_thold:
            continue

        bx = p[0] / bsize
        by = p[1] / bsize
        mp[by, bx] += 1
        
    return mp
