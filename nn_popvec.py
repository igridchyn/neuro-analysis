#!/usr/bin/env python3

from sys import argv
import sys
import numpy as np
import os
from iutils_p3 import *
import multiprocessing
import matplotlib as mpl
from matplotlib import pyplot as plt
from scipy import stats
from scipy.signal import savgol_filter
from tracking_processing_p3 import *
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, mean_squared_error, median_absolute_error
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVR
from scipy.interpolate import interp1d
from sklearn.decomposition import PCA
from sklearn.decomposition import FastICA
from mpl_toolkits.mplot3d import Axes3D
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.neighbors import KernelDensity, KDTree
from sklearn.manifold import SpectralEmbedding
from sklearn.preprocessing import StandardScaler
from scipy.spatial import distance_matrix
import torch
from torch.utils.data import Dataset, DataLoader
import xgboost as xgb
from mind import mind_ensemble

def binary_acc(y_pred, y_test):
    y_pred_tag = torch.round(torch.sigmoid(y_pred))

    correct_results_sum = (y_pred_tag == y_test).sum().float()
    acc = correct_results_sum/y_test.shape[0]
    acc = torch.round(acc * 100)
    
    return acc

## train data
class trainData(Dataset):
    
    def __init__(self, X_data, y_data):
        self.X_data = X_data
        self.y_data = y_data
        
    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]
        
    def __len__ (self):
        return len(self.X_data)

## test data    
class testData(Dataset):
    
    def __init__(self, X_data):
        self.X_data = X_data
        
    def __getitem__(self, index):
        return self.X_data[index]
        
    def __len__ (self):
        return len(self.X_data)

def plot2or3D(data):
        # colormap whl-based
        penv = 0
        low = np.percentile(whl[env==penv,0], 2) #       0/166 1217; 0/188 1220
        high = np.percentile(whl[env==penv,0], 98) #  136/304 1217; 156/347 1220
        print('low/high', low, high)
        # range -0.8 to 0.6
        norm = mpl.colors.Normalize(vmin=low, vmax=high)
        cmap = mpl.cm.jet
        m = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
        sub = env == penv

        if data.shape[1] == 2:     
#            plt.scatter(data[:,0], data[:,1], c=env, s=2)
            plt.scatter(data[sub,0], data[sub,1], c=m.to_rgba(whl[sub,0]), s=2)
        else:
            fig = plt.figure(1, figsize=(4, 3))
            plt.clf()
            ax = Axes3D(fig)
            data =data[sub,:]
            #ax.scatter(data[:,0], data[:,1], data[:,2], c =env)
            ax.scatter(data[:,0], data[:,1], data[:,2], c=m.to_rgba(whl[sub,0]))
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 
        plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False) 
        plt.tight_layout()
        plt.show()

#===================================================================================================================================================================================================

if len(argv) < 6:
    print('USAGE: (1)<base for clu/res> (2)<whl> (3)<staring sample or session number (1-based)> (4)<end sample or session number (1-based)> (5)<env sep> (6)<stat output file>')
    print('     Neural network binary classifier of population vectors')
    exit(0)

argvraw = argv[:]
argv = resolve_vars(argv, False)

ENV_SEP = float(argv[5])

if argv[1][-1] != '.':
    argv[1] = argv[1] + '.'

CR_BASE = argv[1]
tstart =    int(argv[3])
tend =      int(argv[4])

if tstart < 50 and tstart > 0:
    print('INTERPRET TSTART AS DURATIONS OF X FIRST SESSIONS (1-BASED), TAKE DURAITONS FROM tet0/session_shifts.txt')
    ssfile = 'session_shifts.txt' if os.path.isfile('session_shifts.txt') else 'tet0/session_shifts.txt'
    ss = np.loadtxt(ssfile, dtype=int)
    tstart = ss[tstart - 1]

if tend < 50 and tend > 0:
    print('INTERPRET TSTART AS DURATIONS OF X FIRST SESSIONS (1-BASED), TAKE DURAITONS FROM tet0/session_shifts.txt')
    ssfile = 'session_shifts.txt' if os.path.isfile('session_shifts.txt') else 'tet0/session_shifts.txt'
    ss = np.loadtxt(ssfile, dtype=int)
    tend = ss[tend - 1]

# can use 480 sampling rate here byt need to be cautious
WHL_SR = 480
whl = whl_to_pos(open(argv[2]), False)
# MAKES WORSE!
#whl = smooth_whl(whl)
whl = np.array(whl)

if os.path.isfile(CR_BASE + 'clures.npy'):
    [clu, res] = np.load(CR_BASE + 'clures.npy')
else:
    clu = np.loadtxt(CR_BASE + 'clu', dtype = int)
    res = np.loadtxt(CR_BASE + 'res', dtype = int)
    np.save(CR_BASE + 'clures', [clu, res])
print('LOADED CLU/RES')

nclu = max(clu)

# cut only data in interval
ires_start = np.argmax(res > tstart)
ires_end = np.argmin(res < tend)
if ires_end < 1:
    print('WARNING: using end of all res and right bound')
    ires_end = len(res) - 1

iwhl_start = tstart // 480
iwhl_end = tend // 480

res = res[ires_start:ires_end]
res -= res[0]
clu = clu[ires_start:ires_end]
whl = whl[iwhl_start:iwhl_end]
print('Unknown pos in interval of interest %.2f%%' % (np.sum(whl[:,0] == 0)/len(whl)*100))
speed = whl_to_speed(whl)
# DEBUG
#plt.plot(speed)
#speed = np.array(speed)
#plt.hist(speed, bins=np.arange(0, 20, 0.25))
#speed = np.array(speed)
#plt.show()
print('Speed=0 at %.2f%%' % (np.sum(speed==0)/len(speed) * 100))
#speed_int = interp1d(np.where(speed>0)[0], speed[speed>0], kind = 'cubic', fill_value="extrapolate")
#speed = speed_int(range(len(speed)))

# population vectors or load
pathpops = CR_BASE + str(tstart) + '-' + str(tend) + '.pops.npy'
if os.path.isfile(pathpops):
    print('LOAD POPULATION VECTORS')
    pops = np.load(pathpops)
else:
    print('COMPUTE POPULATION VECTORS')
    win = 2400
    t_wbeg = 0
    ires = 0
    pops = np.zeros((res[-1] // win, nclu + 1))
    while t_wbeg < res[-1] - win:
        ipop = t_wbeg // win
        while ires<len(res) and res[ires] < t_wbeg + win:
            pops[ipop, clu[ires]] += 1
            ires += 1
        t_wbeg += win
    np.save(pathpops, pops)

# append whl (env), filter by speed!
# TODO: interpolate env!
THOLD_SPEED = 2 # might be cm/s /3 <<<<<<<<<< ?
MIN_RATE = 0.5 # Hz 0.75 - too much?; 0.5 - Good
env = (whl[:,0] > ENV_SEP).astype(int)
env[whl[:,0] < 0.5] = -1
# fill gaps of unkown environment of max 1 min duration; may still ignore first gap!
MAX_GAP = 60 * 50
ienv = 1
while ienv < len(env):
    if env[ienv] < 0:
        gapstart = ienv
        while ienv < len(env) and  env[ienv] < 0:
            ienv += 1

        # if same env before/after and gap tolerable
        if ienv < len(env) and env[gapstart-1] == env[ienv] and ienv - gapstart < MAX_GAP:
            env[gapstart:ienv] = env[gapstart-1]
    ienv += 1

# wilter our by speed
env[speed < THOLD_SPEED] = -1
env = env[::5]
whl = whl[::5]

# align
TOLER_DIFF = 350
if len(env) > len(pops):
    if len(env) - len(pops) <= TOLER_DIFF:
        print('WARNING: difference in pop/whl len <= 10')
        h = (len(env) - len(pops)) // 2
        dh = len(env) - len(pops) - h
        env = env[h:-dh]
        whl = whl[h:-dh]
        print(len(env))
    else:
        print('ERROR: difference in pop/whl len > 10')
# align
if len(env) < len(pops):
    if len(pops) - len(env) <= TOLER_DIFF:
        print('WARNING: difference in pop/whl len <= 10')
        h = (len(pops) - len(env)) // 2
        dh = len(pops) - len(env) - h
        pops = pops[h:-dh, :]
        print(len(env))
    else:
        print('ERROR: difference in pop/whl len > 10')

print('Known pos && > ST: %.2f%%' % (np.sum(env >= 0)/len(env)*100))

# only when env is known
pops = pops[env >= 0, :]
whl = whl[env >= 0]
env = env[env >= 0]






# save both
pathpops = CR_BASE + str(tstart) + '-' + str(tend) + '.pops_envs.npz'
np.savez(pathpops, pops=pops, envs=env)

# standardize
np.set_printoptions(threshold=sys.maxsize)
totals_spikes = np.sum(pops, axis=0)
indrate = totals_spikes > MIN_RATE * res[-1] / 24000
print('%d cells pass min rate criterion' % sum(indrate))
pops = pops[:, indrate]
print('WARNING: SQUARE ROOT TRANSFORMING AND STANDARDIZING POPULATION VECTOR FEATURES!')
pops = np.sqrt(pops)
pops = (pops - np.mean(pops, axis=0)) / np.std(pops, axis=0)

# get rid of nans
nans = np.isnan(np.std(pops, axis=0))
print('Get rid of %d nan cols' % np.sum(nans))
pops = pops[:,~nans]


# ===============================================================================[ PCA ]==============================================================================================
# TESTS
#DOPCA = False
DOPCA = True
PLOT_PCA = False
if DOPCA:
    npcadim = 2 #pops.shape[1]
    pca = PCA(n_components=npcadim)
    #pca = FastICA(n_components=npcadim)
    pca.fit(pops)
    pops_pc = pca.transform(pops)

    ssuf =  'p' if 'plfe' in argvraw[-2] else 'l'

    pca_var = pca.explained_variance_
    np.savetxt('tmp_pca_sqrt_%s_e1.txt' % ssuf, np.cumsum(pca_var))
#    plt.show()
#    exit(0)

    # means and median normalized
    if False:
        pca_mean = np.sum(pca.explained_variance_ratio_ * np.arange(1, pops.shape[1] + 1))
        pca_median = np.argmax(np.cumsum(pca.explained_variance_ratio_) > 0.5)
        np.savetxt('tmp_pca_sqrt_mean_%s.txt' % ssuf, [pca_mean])
        np.savetxt('tmp_pca_sqrt_median_%s.txt' % ssuf, [pca_median])
        exit()

    if PLOT_PCA:
        if npcadim == 2:
        #    plt.scatter(pops_pc[env==0,0], pops_pc[env==0,1])
        #    plt.scatter(pops_pc[env==1,0], pops_pc[env==1,1], color='red')
            plt.scatter(pops_pc[:,0], pops_pc[:,1], c=env, s=2)
        else:
            fig = plt.figure(1, figsize=(4, 3))
            plt.clf()
            ax = Axes3D(fig)
            ax.scatter(pops_pc[:,0], pops_pc[:,1], pops_pc[:,2], c = env)    
        #plt.show()
        #print('WARNING: USE PCA FOR FURTHER MODELS')
        #pops = pops_pc
        #exit(0)

# KL-divergence of first PC/IC distributions for the 2 classes
# fit KDE -> calculate on grid -> divergence
def grid_search(data, space):
    grid = GridSearchCV(KernelDensity(kernel='gaussian'), {'bandwidth': space}, cv=5, n_jobs=-1)
    return grid.fit(data).best_params_['bandwidth']
def parallel_score_samples(kde, samples, thread_count=int(0.95 * multiprocessing.cpu_count())):
    with multiprocessing.Pool(thread_count) as p:
        return np.concatenate(p.map(kde.score_samples, np.array_split(samples, thread_count)))

# ===============================================================================[ KDE ]==============================================================================================
DOKDA = False
if DOKDA:
    bw0 = grid_search(pops_pc[env==0,:], np.linspace(0,1, 101))
    bw1 = grid_search(pops_pc[env==1,:], np.linspace(0,1, 101))
    print('KDE bws:', bw0, bw1)
    kde0 = KernelDensity(kernel='gaussian', bandwidth=bw0).fit(pops_pc[env==0,:])
    kde1 = KernelDensity(kernel='gaussian', bandwidth=bw1).fit(pops_pc[env==1,:])
    xmin, xmax = -10, 10
    ymin, ymax = -10, 10
    # 1000 was similar results but longer
    xx, yy = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = np.vstack([xx.ravel(), yy.ravel()]).transpose()
    print('Positions shape', positions.shape)
    #d1 = kde0.score_samples(positions)
    d0 = parallel_score_samples(kde0, positions)
    #d2 = kde1.score_samples(positions)
    d1 = parallel_score_samples(kde1, positions)
    kldiv = stats.entropy(d0, d1)
    print('KL-divergence:', kldiv)
    #if len(argv) > 6: open(argv[6], 'w').write(str(kldiv) + '\n')
    exit(0)

# ===============================================================================[ MIND ]==============================================================================================
# https://github.com/JoramKeijser/MIND/blob/master/notebooks/Toy_data.ipynb
#stds = np.std(pops, axis=0)
#print(np.std(pops, axis=0))
#print('WARNING, FILTER SMALL VARIANCE')
#pops = pops[:, stds > 0.1]

man_dim = 3
path_mind = CR_BASE + str(tstart) + '-' + str(tend) + '.whl_lin.pops_mind%d.npy' % man_dim
#DOMIND = True
DOMIND = False
print('MIND: looking for file', path_mind)
if os.path.isfile(path_mind + '.txt'):
    pops_mind = np.loadtxt(path_mind + '.txt')
    print('WARINIG: IGNORE 4 POINTS IN pops_mind')
    pops_mind = pops_mind[2:-2]
elif DOMIND:
    print('LEARN MIND MANIFOLD')
    print('nans:', np.sum(np.isnan(pops)))
    m = mind_ensemble(pops, manifold_dim=man_dim, n_trees=100, seed=123)
    m.learn_coordinates()
    np.save(path_mind, m.y)
    pops_mind = m.y

#PLOTMIND = True
PLOTMIND = False
if PLOTMIND:
    plot2or3D(pops_mind)
#    exit(0)
#    f, ax = plt.subplots(1, 2)
#    ax[0].imshow(pops_mind.P)
#    ax[1].imshow(pops_mind.D)
#    ax[0].set_title("Transition probabilities");
#    ax[1].set_title("Pairwise distances");
#    plt.scatter(pops_mind.y[:,0], pops_mind.y[:,1])
#    plt.xlabel("Manifold Dim. 1")
#    plt.ylabel("Manifold Dim. 2");
#    plt.show()

# ===============================================================================[ LEM - LAPLACIAN EIGENMAPS ]==============================================================================================
# Laplacian Eigenmaps: non-linear dimensionality reduction, used in Ziv's analysis

#DOLEM = False
DOLEM = True

if DOLEM:
    ncomp_lem = 3
    #lem_var_ex = []
 #   path_lem_full = CR_BASE + str(tstart) + '-' + str(tend) + '.whl_lin.pops_lem%d.npy' % pops.shape[1]
  #  pops_lem_full = np.load(path_lem_full)
#    trace_full = np.trace(np.cov(pops_lem_full.transpose()))

    for ncomp_lem in [ncomp_lem]: #list(range(1,10)):
        path_lem = CR_BASE + str(tstart) + '-' + str(tend) + '.whl_lin.pops_lem%d.npy' % ncomp_lem
        if os.path.isfile(path_lem):
            print('Load Laplacian eigenmaps embedding...')
            pops_lem = np.load(path_lem)
        else:
            print('Build Laplacian eigenmaps embedding...')
            embedding = SpectralEmbedding(n_components=ncomp_lem, n_jobs=-1)
            pops_lem = embedding.fit_transform(pops)
            np.save(path_lem, pops_lem)
        #plot2or3D(pops_lem)
       
#        if ncomp_lem > 1: 
#            lem_var_ex.append(np.trace(np.cov(pops_lem.transpose())) / trace_full)
#        else:
#            lem_var_ex.append(np.var(pops_lem) / trace_full)
    
#plt.plot(range(1, len(lem_var_ex)+1), lem_var_ex)
#plt.show()
#exit(0)

#-------------------------------------------------------[ GEOMETRY MAPPING ON FEATURES ]--------------------------------------------------------------------

DO_GEOMAP = False

if DO_GEOMAP:
    print('Calculate distance matrices...', end='')
    whl_d = np.vstack((distance_matrix(whl[env == 0], whl[env == 0]).flatten().reshape(-1,1), distance_matrix(whl[env == 1], whl[env == 1]).flatten().reshape(-1,1))).flatten()
    pops_d = np.vstack((distance_matrix(pops_lem[env == 0], pops_lem[env == 0]).flatten().reshape(-1,1), distance_matrix(pops_lem[env == 1], pops_lem[env == 1]).flatten().reshape(-1,1))).flatten()
    #pops_d = np.vstack((distance_matrix(pops_pc[env == 0], pops_pc[env == 0]).flatten().reshape(-1,1), distance_matrix(pops_pc[env == 1], pops_pc[env == 1]).flatten().reshape(-1,1))).flatten()
    #pops_d = np.vstack((distance_matrix(pops_mind[env == 0], pops_mind[env == 0]).flatten().reshape(-1,1), distance_matrix(pops_mind[env == 1], pops_mind[env == 1]).flatten().reshape(-1,1))).flatten()
    print('DONE')
    #plt.scatter(whl_d, pops_d)
    d2d = []
    maxdist = 175
    valid_dist = []
    for d in range(maxdist): # 250/200/100
        if np.sum((whl_d > d) & (whl_d < d + 1)) > 10:
            d2d.append(np.mean(pops_d[(whl_d > d) & (whl_d < d + 1)]))
            valid_dist.append(d)
    #plt.hist2d(whl_d, pops_d, bins=[100,100])
    print('Pearson correla: %.3f' % stats.pearsonr(whl_d, pops_d)[0])
    print('Rank order corr: %.3f' % stats.spearmanr(whl_d, pops_d)[0])
    print('Avg. pearson correla: %.3f' % stats.pearsonr(valid_dist, d2d)[0])
    print('Avg. rank order corr: %.3f' % stats.spearmanr(valid_dist, d2d)[0])
    d2d = savgol_filter(d2d, 11, 3)
    plt.plot(range(len(d2d)), d2d)
    strip_axes(plt.gca())
    plt.tight_layout()
    plt.show()
    #exit(0)


#------------------------------------------------------------[ RENORM ]--------------------------------------------------------------

#print('WARNING: USING REDUCED DIMENSIONALITY REPRESENTATION FOR FURTHER PREDICTIONS + RENORM')
#pops = pops_lem
#pops = pops_pc
#pops = pops_mind
#pops = (pops - np.mean(pops, axis=0)) / np.std(pops, axis=0)



# predict position in two environments! / ENV_SEP use linear/normalized posotion ->
pops0 = pops[env == 0]
pops1 = pops[env == 1]
whl0 = whl[env == 0,0]
whl1 = whl[env == 1,0]
whl0 = whl0.reshape(-1,1)
whl1 = whl1.reshape(-1,1)
st_scaler = StandardScaler()
whl0 = st_scaler.fit_transform(whl0)
print('SCALER MEAN/STD 1', st_scaler.mean_, st_scaler.var_**0.5)
whl1 = st_scaler.fit_transform(whl1)
print('SCALER MEAN/STD 2', st_scaler.mean_, st_scaler.var_**0.5)
whl0 = whl0.flatten()
whl1 = whl1.flatten()


# default max_depth = 2
# ===============================================================================[ RANDOM FOREST ]==============================================================================================
rf_regr0 = RandomForestRegressor(max_depth=5, random_state=0)
rf_regr1 = RandomForestRegressor(max_depth=5, random_state=0)
pops_train0, pops_test0, whl_train0, whl_test0 = train_test_split(pops0, whl0, test_size=0.25, random_state=142) # 42 used for a long time
pops_train1, pops_test1, whl_train1, whl_test1 = train_test_split(pops1, whl1, test_size=0.25, random_state=142) # 42 used for a long time
rf_regr0.fit(pops_train0, whl_train0)
rf_regr1.fit(pops_train1, whl_train1)
whl_pred0 = rf_regr0.predict(pops_test0)
mae0 = median_absolute_error(whl_test0, whl_pred0)
whl_pred1 = rf_regr1.predict(pops_test1)
mae1 = median_absolute_error(whl_test1, whl_pred1)
print('MAE (RandForReg):  %.2f / %.2f' % (mae0, mae1))



# ===============================================================================[ SVR ]==============================================================================================
#param = {'kernel' : ('linear', 'poly', 'rbf', 'sigmoid'),'C' : [1,5,10,20],'degree' : [3,5,7,9],'coef0' : [0.01,0.1,0.5,1,2],'gamma' : ('auto','scale'), 'epsilon':[0.1, 0.2, 0.5]} # SUPER LONG SEARCH TIME -> didn't finish
#param = {'kernel' : ['linear'],'C' : [1,5,10,20],'degree' : [3,5,7,9],'coef0' : [0.01,0.1,0.5,1,2],'gamma' : ('auto','scale'), 'epsilon':[0.1, 0.2, 0.5]} # {'C': 20, 'coef0': 0.01, 'degree': 3, 'epsilon': 0.5, 'gamma': 'auto', 
#param = {'kernel' : ['linear'],'C' : [80, 100, 120],'degree' : [1,2],'coef0' : [0.0001, 0.001],'gamma' : ('auto','scale'), 'epsilon':[0.5, 0.7, 0.9]} # {'C': 80, 'coef0': 0.001, 'degree': 1, 'epsilon': 0.7, 'gamma': 'auto'} => {'C': 120, 'coef0': 0.0001, 'degree': 1, 'epsilon': 0.7, 'gamma': 'auto'}
#param = {'kernel' : ['linear'],'C' : [120, 200, 300],'degree' : [1,2],'coef0' : [0, 0.0001],'gamma' : ('auto','scale'), 'epsilon':[0.7]} # LME-3: 0.7/300/0
#param = {'kernel' : ['poly'],'C' : [1,5,10,20],'degree' : [3,5,7,9],'coef0' : [0.01,0.1,0.5,1,2],'gamma' : ('auto','scale'), 'epsilon':[0.1, 0.2, 0.5]} # LME-3: this seems enormous amound to calculate
#param = {'kernel' : ['poly'],'C' : [1,5,10],'degree' : [3,5,7], 'gamma' : ('auto','scale'), 'epsilon':[0.1, 0.2, 0.5]} # LME-3: {'C': 5, 'degree': 3, 'epsilon': 0.5, 'gamma': 'auto', 'kernel': 'poly'}
#param = {'kernel' : ['poly'],'C' : [2,3,5,7],'degree' : [2,3,4], 'gamma' : ['auto'], 'epsilon':[0.5, 0.7, 0.9]} # LME-3: {'C': 5, 'degree': 3, 'epsilon': 0.5, 'gamma': 'auto', 'kernel': 'poly'}             <<<<<< best with poly kernel
#param = {'kernel' : ['poly'],'C' : [0.5, 1, 2],'degree' : [2,3,4], 'gamma' : ['auto'], 'epsilon':[0.5, 0.7, 0.9]} # MIND-3:  2,3,0.7
#param = {'C' : [1,5,10], 'gamma' : ('auto','scale'), 'epsilon' : [0.1, 0.2, 0.5]}  # env 0 : c=1, eps = 0.1, gamm = scale
#param = {'C' : [1,5,10], 'gamma' : ('auto','scale'), 'epsilon' : [0.1, 0.2, 0.5]}  # MIND-3: 1, 0.5
param = {'C' : [0.1, 0.2, 0.5, 1], 'gamma' : ('auto','scale'), 'epsilon' : [0.5, 0.7, 0.9]}  # MIND-3: 1, 0.5 => FIX
#param = {'C' : [0.2, 0.5, 1, 2], 'gamma' : ('auto','scale'), 'epsilon' : [0.05, 0.1, 0.2]} # env 0 : c=1, eps = 0.05
#param = {'C' : [0.2, 0.5, 1, 2], 'gamma' : ('auto','scale'), 'epsilon' : [0.01, 0.02, 0.05]} # env 0 : c=1, eps=0.02;              non-reduced: C=2, epsilon=0.05
#param = {'C' : [2, 5, 10], 'gamma' : ('auto','scale'), 'epsilon' : [0.05, 0.1, 0.2]} #=> 2, 0.05, scale for non-reduced; 10, 0.2, auto for LME-3
#param = {'C' : [20, 50, 80], 'gamma' : ('auto','scale'), 'epsilon' : [0.1, 0.2, 0.5]} # 20, 0.2, auto for LME-3 => 50, 0.2, scale;
#param = {'C' : [20, 50, 80], 'gamma' : ('auto','scale'), 'epsilon' : [0.1, 0.2, 0.5], 'kernel' : ('linear', 'poly', 'rbf', 'sigmoid')} # LME-3: rbf with params above

GRID_SVR = False
#GRID_SVR = True
if GRID_SVR:
    modelsvr = SVR()
    grids = GridSearchCV(modelsvr, param, cv=5, n_jobs=-1)
    print('Grid search SVR')
    grids.fit(pops0, whl0)
    print('Grid CV best params:', grids.best_params_)

#pset = {'C':2.0, 'epsilon':0.05, 'gamma':'scale'} # non-reduced dim
pset = {'C':50.0, 'epsilon':0.2, 'gamma':'scale'} if not GRID_SVR else grids.best_params_ # LEM-3, RBF kernel
#pset = {'C':200, 'coef0':0, 'degree':3, 'kernel':'linear', 'epsilon':0.7, 'gamma':'auto'} # best linear kernel for LEM-3
svr_reg0 = SVR(C=pset['C'], epsilon=pset['epsilon'], gamma=pset['gamma']) # 1220, probablt reduced dim: C=1.0, epsilon = 0.02
svr_reg1 = SVR(C=pset['C'], epsilon=pset['epsilon'], gamma=pset['gamma']) # 1220, probablt reduced dim: C=1.0, epsilon = 0.02
svr_reg0.fit(pops_train0, whl_train0)
svr_reg1.fit(pops_train1, whl_train1)
whl_pred0 = svr_reg0.predict(pops_test0)
mae0 = median_absolute_error(whl_test0, whl_pred0)
whl_pred1 = svr_reg1.predict(pops_test1)
mae1 = median_absolute_error(whl_test1, whl_pred1)
mean_mae = np.mean((mae0, mae1))
print('MAE (SVR):  %.3f / %.3f      average: %.3f' % (mae0, mae1, mean_mae))
if len(argv) > 6: open(argv[6], 'w').write(str(mean_mae) + '\n')

# ===============================================================================[ XGBOOST ]==============================================================================================
DOXGBOOST = False
if DOXGBOOST:
    print('Train XGBoost model')
    dtrain0 = xgb.DMatrix(pops_train0, label=whl_train0)
    dtest0 = xgb.DMatrix(pops_test0, label=whl_test0)
    dtrain1 = xgb.DMatrix(pops_train1, label=whl_train1)
    dtest1 = xgb.DMatrix(pops_test1, label=whl_test1)
    #param = {'max_depth': 2, 'eta': 1, 'objective': 'reg:squarederror', 'nthread':12}
    #param = {'max_depth': 4, 'gamma':0.5, 'eta': 1, 'objective': 'reg:squarederror', 'nthread':12}
    # eta pretty solid 0.3
    # max_depth: 6 / 8 / 10
    # subsample: no
    # lambda: 2,4 worse
    # booster: gblinear bad X 2, dart similar
    # gamma: 0
    #param = {'tree_method':'gpu_hist', 'eta':0.1, 'max_depth':7, 'gamma':0.2} # eta 0.1-0.3, gamma: 0.2-0.5, max depth 6-7
    #evallist0 = [(dtest0, 'eval'), (dtrain0, 'train')]
    #evallist1 = [(dtest1, 'eval'), (dtrain1, 'train')]
    #num_round = 50
    pset = {'learning_rate':0.05, 'gamma':0.05, 'max_depth':12} # LME-3
    #pset = {'learning_rate':0.1, 'gamma':0.2, 'max_depth':23} # full 1220
    xgb_regr0 = xgb.XGBRegressor(tree_method = 'gpu_hist', learning_rate=pset['learning_rate'], n_estimators=100, objective='reg:squarederror', nthread=1, verbosity=0, gamma=pset['gamma'], max_depth=pset['max_depth']) # max_depth 7
    xgb_regr1 = xgb.XGBRegressor(tree_method = 'gpu_hist', learning_rate=pset['learning_rate'], n_estimators=100, objective='reg:squarederror', nthread=1, verbosity=0, gamma=pset['gamma'], max_depth=pset['max_depth'])
    #bst0 = xgb.train(param, dtrain0, num_round, evallist0, early_stopping_rounds=3, n_estimators=100)
    bst0 = xgb_regr0.fit(pops_train0, whl_train0, eval_set=[(pops_test0, whl_test0)], early_stopping_rounds=3)
    #bst1 = xgb.train(param, dtrain1, num_round, evallist1, early_stopping_rounds=3)
    bst1 = xgb_regr1.fit(pops_train1, whl_train1, eval_set=[(pops_test1, whl_test1)], early_stopping_rounds=3)
    whl_pred0 = bst0.predict(pops_test0)
    #whl_pred1 = bst1.predict(dtest1)
    whl_pred1 = bst1.predict(pops_test1)
    mae0 = median_absolute_error(whl_test0, whl_pred0)
    mae1 = median_absolute_error(whl_test1, whl_pred1)
    print('XGBoost MAE: %.3f / %.3f;        average = %.3f' % (mae0, mae1, np.mean([mae0, mae1])))


    xgbr = xgb.XGBRegressor(tree_method = 'gpu_hist', learning_rate=0.02, n_estimators=100, objective='reg:squarederror', nthread=1, verbosity=2) # was n_estimators 600; set nrounds num_round/nrounds/early_stoping_rounds doesn't work
    #params = {  'min_child_weight': [1, 5, 10], 'gamma': [0.5, 1, 1.5, 2, 5], 'subsample': [0.6, 0.8, 1.0], 'colsample_bytree': [0.6, 0.8, 1.0], 'max_depth': [3, 4, 5] }
    #params = {'eta':[0.1,0.2,0.3,0.4], 'gamma': [0.2, 0.5, 1],  'max_depth': [6,7,8,9]} # => {'max_depth': 7, 'gamma': 0.2, 'eta': 0.1} for first 3 LEM components!     {'max_depth': 9, 'gamma': 0.2, 'eta': 0.1} for complete data; 0.1,0.2,7 for reduced data
    #params = {'eta':[0.02, 0.05, 0.1], 'gamma': [0.05, 0.1, 0.2],  'max_depth': [6,7,8]} # LME-3: 0.02, 0.05, 8
    #params = {'eta':[0, 0.01, 0.02], 'gamma': [0.01, 0.02, 0.05],  'max_depth': [8, 9, 10]} # LME-3: 0, 0.05, 10
    params = {'eta':[0], 'gamma': [0.05],  'max_depth': [10, 12, 14, 16]} # LME-3 => 12
    #params = {'eta':[0.1], 'gamma': [0.2],  'max_depth': [8,9,10,11,12,13]} # > max depth 13
    #params = {'eta':[0.1], 'gamma': [0.2],  'max_depth': [23, 27, 31, 35, 39, 43]} # > max depth 13 -> 23  -> (not enough memory if too much depth!, decrease number of concurrent jobs) -> FAIL (not enough memory ...)

        # wuth 100 estimators and num_round = 100:
    # opt results: wityh gamma 0.5, opt depth = 4
    # potentially useful parameters: booster (general param, just run grid few times, gbtree is default); 
 
XGB_CV = False
#XGB_CV = True
if XGB_CV: 
    npar = 1
    for k,v in params.items(): npar *= len(v) 
    random_search = RandomizedSearchCV(xgbr, param_distributions=params, n_iter=npar, scoring='neg_median_absolute_error', n_jobs=12, cv=5, verbose=1, random_state=1001 )
    random_search.fit(pops_train0, whl_train0)
    print('XGBoost best random search params:', random_search.best_params_)

#grid_search_xgb = GridSearchCV(xgbr, param_grid=params, scoring='neg_median_absolute_error', n_jobs=12, cv=2)
#grid_search_xgb.fit(pops_train0, whl_train0)
#print('XGBoost best grid params:', grid_search_xgb.best_params_)

# for gpu support specify gpu_hist as tree_method paraemter : tree_method='gpu_hist', gpu_id=0 for sklearn interface



# ===========================================================================================================[ BINARY CLASSIFIERS ]===================================================================================================================
env = np.reshape(env, (-1, 1))
print('Pops dims', pops.shape)
print('Env shape', env.shape)

pops_train, pops_test, env_train, env_test = train_test_split(pops, env, test_size=0.25, random_state=142) # 42 used for a long time

# ===========================================================================================================[ LOGISTIC REGRESSION ]===================================================================================================================
clf = LogisticRegression(random_state=0).fit(pops_train, env_train)
env_pred = clf.predict(pops_test)
cm = confusion_matrix(env_test, env_pred)
asc = accuracy_score(env_test, env_pred)
print('Confusion matrix (LogReg):', cm)
print('Accuracy score (LogReg):  %.2f%%' % (asc*100))

# ===========================================================================================================[ RANDOM FOREST ]===================================================================================================================
DORF = False
if DORF:
    clf_rf=RandomForestClassifier(n_estimators=1000).fit(pops_train, env_train)
    env_pred = clf_rf.predict(pops_test)
    cm = confusion_matrix(env_test, env_pred)
    asc = accuracy_score(env_test, env_pred)
    print('Confusion matrix (RandFor):', cm)
    print('Accuracy score (RandFor): %.2f%%' % (asc*100))

    #if len(argv) > 6: open(argv[6], 'w').write(str(asc*100) + '\n')
    #exit(0)

# ===========================================================================================================[ NEURAL NETWORKS ]===================================================================================================================

N, D_in, H, D_out = len(pops_train0), pops_train0.shape[1], 5, 1           # was 64, 1000, 100, 10;    WORKED WITH 10 HIDDEN; 30 - OVERFIT;   15 FOR REGRESSION
BATCH_SIZE = 256
H0 = 10


# FOR REGRESSION: Linear -> ReLU -> Linear

# FOR REGRESSION: Linear(D_in, H) + ReLU + Linear(H, D_out)
# AUTOENCODERS  : Linear(D_in, H) + ReLU + Linear(H, D_in)
model = torch.nn.Sequential(
    torch.nn.Linear(D_in, H0),
    torch.nn.ReLU(),

    torch.nn.Linear(H0, H),
    torch.nn.ReLU(),
    torch.nn.Linear(H, H0),
    torch.nn.ReLU(),

#    torch.nn.BatchNorm1d(H),
    torch.nn.Linear(H0, D_in), # this was end originally
#    torch.nn.ReLU(),
    torch.nn.Sigmoid()

#    torch.nn.Dropout(p=0.1)
)

# Try initializations
torch.nn.init.xavier_uniform_(model[0].weight)
torch.nn.init.xavier_uniform_(model[2].weight)
torch.nn.init.xavier_uniform_(model[4].weight)
torch.nn.init.xavier_uniform_(model[6].weight)

loss_fn = torch.nn.MSELoss(reduction='sum')         # for regression - position / autoencoder
#loss_fn = torch.nn.BCEWithLogitsLoss()             # for BINARY

# regression: 1e-6 too small; 1e-3 ok
learning_rate = 1e-3 # CLASSIFIERS: 1e-4 for MSELoss; 1e-2 for BCEWithLogitsLoss;       REGRESSION: 1e-3        AUTOENCODER: 1e-3

print('CUDA AVAILABLE:', torch.cuda.is_available())
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)

# using Data Loader - binary
#train_data = trainData(torch.FloatTensor(pops_train), torch.FloatTensor(env_train))
#test_data = testData(torch.FloatTensor(pops_test))
#train_loader = DataLoader(dataset=train_data, batch_size=BATCH_SIZE, shuffle=True)
#test_loader = DataLoader(dataset=test_data, batch_size=1)

# using Data Loader - REGRESSION, position env 0
#train_data = trainData(torch.FloatTensor(pops_train0), torch.FloatTensor(whl_train0.reshape(-1,1)))
#test_data = testData(torch.FloatTensor(pops_test0))
train_data = trainData(torch.FloatTensor(pops_train0), torch.FloatTensor(pops_train0))
test_data = testData(torch.FloatTensor(pops_train0))
train_loader = DataLoader(dataset=train_data, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(dataset=test_data, batch_size=1) #DataLoader(dataset=test_data, batch_size=1)

optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
#optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)

model.train()
# Regression: 1000 for 1e-3
EPOCHS = 1500 # 100 for batch 256 and learning rate 1e-3; 500-1000 for learning rate 1e-4;
for e in range(1, EPOCHS+1):

    epoch_loss = 0
    epoch_acc = 0

    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)

        y_pred = model(X_batch)

        loss = loss_fn(y_pred, y_batch)
        acc = binary_acc(y_pred, y_batch)

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        epoch_loss += loss.item()
        epoch_acc += acc.item()

    if not e % 50:
        print(f'Epoch {e+0:03}: | Loss: {epoch_loss/len(train_loader):.5f} | Acc: {epoch_acc/len(train_loader):.3f}')
           
y_pred_list = []
model.eval()
with torch.no_grad():
    for X_batch in test_loader:
        X_batch = X_batch.to(device)
        y_test_pred = model(X_batch)

        # ONLY FOR CLASSIFIER
#        y_test_pred = torch.sigmoid(y_test_pred)
#        y_pred_tag = torch.round(y_test_pred)
#        y_pred_list.append(y_pred_tag.cpu().numpy())

        y_pred_list.append(y_test_pred.cpu().numpy())

y_pred_list = [a.squeeze().tolist() for a in y_pred_list]
y = y_pred_list

# BINARY
#cm = confusion_matrix(env_test, y)
#asc = accuracy_score(env_test, y)
#print('Confusion matrix:', cm)
#print('Accuracy score: %.2f' % (asc * 100))

#gt = whl_test0
gt = pops_train0
nn_mae0 = median_absolute_error(gt, y)
print('NN env 0 MAE:', nn_mae0)
nn_mse0 = mean_squared_error(gt, y)
print('NN env 0 MSE:', nn_mse0)

gt = pops_train0
s1 = np.random.choice(range(len(gt)), 300)
s2 = np.random.choice(range(len(gt)), 300)
nn_mse0 = mean_squared_error(gt[s1], gt[s2])
print('Rand MSE:', nn_mse0)
