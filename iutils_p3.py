from matplotlib import rcParams
from os.path import isdir, dirname, isfile
from os import mkdir, getcwd, strerror
from numpy import array, ndarray
import numpy as np
import ast
import operator as op
from scipy.stats import norm
import statsmodels.api as sm
from matplotlib import pyplot as plt
import os
import re
import warnings

def strip_axes(ax = plt.gca()):
    #ax = plt.gca()
    # remove top and right spines - frame axes
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

def strip_all_axes(ax = plt.gca()):
    #ax = plt.gca()
    # remove top and right spines - frame axes
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)


#============================================  OPTIONAL PARAMETERS  ========================================================
# parse last params - paris of <'-key' 'value'>
def parse_optional_params(oargs):
    dic = {}
    if len(oargs) % 2 == 1:
        raise ValueError("ERROR: number of optional parmeters has to be even")

    for i in range(len(oargs) // 2):
        dic[oargs[2*i][1:]] = oargs[2*i+1]

    return dic

# get dicitionary value
def gdv(dic, key, default = ''):
    return dic[key] if key in dic else default

# get dicitionary value - integer
def gdvi(dic, key, default = ''):
    return int(dic[key] if key in dic else default)

# get dicitionary value - float
def gdvf(dic, key, default = ''):
    return float(dic[key] if key in dic else default)
#===========================================  ADVANCED PARAMETER PARSING  =========================================================
# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

def eval_expr(expr):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    return eval_(ast.parse(expr, mode='eval').body)

def eval_(node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)
#=============================================  READ / WRITE  =======================================================

def line_floats(f):
    return [float(w) for w in f.readline().split(' ')]

def write_list_fmt(l, path, fmt):
    f = open(path, 'w')
    for el in l:
        f.write(fmt % el)
    f.close()

def write_array(a, path):
    f = open(path, 'w')
    for r in a:
        if type(r) == ndarray:
            for e in r:
                f.write('%f ' % e)
        else:
            f.write('%f' % r)
        f.write('\n')
    f.close()

def write_list(l, path):
    if os.path.isfile(path):
        print('ERROR: file exists ', path)
        exit(2234)

    f = open(path, 'w')
    for el in l:
        f.write(str(el) + '\n')
    f.close()

def read_float_list(path):
    f = open(path)
    res = []
    for l in f:
        s = l.split(' ')
        res.append([float(e) for e in s if len(e) > 0 and e!='\n'])
        if len(res[-1]) == 1:
            res[-1] = res[-1][0]

    return res

def read_float_array(path):
    return array(read_float_list(path))

def read_int_list(path):
    l = read_float_list(path)
    if type(l[0]) == type(0.0) or type(l[0]) == type(0):
        return [int(el) for el in l]
    else:
        res = []
        for li in l:
            res.append([int(el) for el in li])
        return res

def read_bool_array(path):
    l = read_int_list(path)
    return np.asarray(l, dtype=np.bool)

def read_int_array(path):
    return array(read_int_list(path))

# ? old about contains unscaled ?
def resolve_vars(args, oldabout = True):
    # substitute variables in for, %{animal} by values from about.txt
    path = 'about_old.txt' if oldabout else 'about.txt'
    if not isfile(path):
        path ='../about_old.txt' if oldabout else '../about.txt'
    if not isfile(path):
        raise ValueError('ERROR: File not found: about.txt')
    
    d = {}
    for line in open(path):
        ws = line.split(' ')
        d[ws[0]] = ws[1][:-1]

    if 'date' in d:
        d['day'] = d['date'][2:]
    # %{FULL} = '_FULL' if current dir contains FULL, '' otherwise
    d['FULL'] = '_FULL' if ('FULL' in getcwd() or isdir(getcwd() + '/9l_FULL')) else ''

    sspath = 'session_shifts.txt'
    if not isfile(sspath):
        # print 'WARNING: session shifts file not found at', getcwd() + '/' + sspath 
        pass 
    else:
        ss = [l[:-1] for l in open(sspath)]
        # DEBUG
        # print 'Session shifts: ', ss
        for i in range(len(ss)):
            d['ss%s' % i] = ss[i]

    # subsitute
    narg = []
    for arg in args:
        while '%{' in arg:
            start = arg.index('{')
            end = arg.index('}')
            var = arg[start + 1 : end]

            if var not in d:
                print('ERROR: value %s not found in about.txt' % var)
                exit(69782)

            arg = arg.replace('%%{%s}' % var, d[var])
            # print 'After replace: ', arg

        narg.append(arg)

    # now resolve expressions
    for i in range(1, len(narg)):
        if any(s in narg[i] for s in '+-/*$') and narg[i] not in '-+' and narg[i][0]=='E':
            narg[i] = str(eval_expr(narg[i][1:]))

    return narg
#======================================  ETC  ==============================================================

def suppress_warnings():
    warnings.filterwarnings("ignore",category = RuntimeWarning)
    warnings.simplefilter(action='ignore', category=FutureWarning)

def fig_save_dir():
    return '/home/igor/resim/_AUTOSAVE/'

def set_print_format():
    np.core.arrayprint._line_width = 220
    float_formatter = lambda x: "%.3f" % x
    np.set_printoptions(formatter={'float_kind':float_formatter}, threshold=1000000)

def exists_or_create(dire):
    dr = dirname(dire)
    if not isdir(dr):
        mkdir(dr)

def set_xticks_off():
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)

def set_yticks_off():
    plt.tick_params(
        axis='y',          # changes apply to the y-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)

def set_ticks_off():
    plt.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)

def set_xticks_font(fs):
    for tick in plt.gca().xaxis.get_major_ticks():
        tick.label.set_fontsize(fs) 

def set_yticks_font(fs):
    for tick in plt.gca().yaxis.get_major_ticks():
        tick.label.set_fontsize(fs) 

def plot_sig(x1, x2, y, sh, sig, fs, ysh=1):
    slw = 4
    plt.plot([x1, x2], [y, y], color='black', linewidth=slw)
    plt.plot([x1, x1], [y-sh, y], color='black', linewidth=slw)
    plt.plot([x2, x2], [y-sh, y], color='black', linewidth=slw)
    plt.text(x1 + (x2 - x1)*0.5, y+ysh, sig, fontsize=fs)
#====================================== PARSE  ==============================================================
def line_to_floats(line, delim = ' '):
    return [float(f) for f in line.split(delim) if len(f) > 1]
def split2lines(s):
    spaces = [m.start() for m in re.finditer(' ', s)]
    ospaces = spaces
    spaces = np.array(spaces)
    spaces -= len(s) / 2
    spaces = np.abs(spaces)
    na = np.argsort(spaces)
    print(s, spaces[na])
    pos = ospaces[na[0]]
    return s[:pos] + '\n' + s[pos+1:]
#====================================== MATH ==============================================================
def p_to_sig_str(p):
        if p > 0.1:
                return 'n.s.'
        elif p > 0.05:
                return 'n.s.' #'^' # for debugging
        elif p > 0.01:
                return '*'
        elif p > 0.005:
                return '**'
        elif p > 0.001:
                return '***'
        else:
                return '****'

def corr_conf_interval(r, n, nstd=1.0):
    z_r = np.arctanh(r)
    # z_r = np.log((1 + r) / (1 - r)) * (np.sqrt(n - 3) / 2)
    #r_low  = norm.sf(z_r - 1.0/np.sqrt(n-3))
    #r_high = norm.sf(z_r + 1.0/np.sqrt(n-3))
    #print z_r, n; # of STD
    r_low = r-np.tanh(z_r - nstd/np.sqrt(n-3))
    r_high = np.tanh(z_r + nstd/np.sqrt(n-3))-r
    return [r_low, r_high]

# of a and b given c
def partial_correlation(a,b,c):
    ind = ~np.isnan(a) & ~np.isnan(b) & ~np.isnan(c)
    
    #a=sm.add_constant(a)
    #b=sm.add_constant(b)

    ma = sm.OLS(a[ind], c[ind])
    mb = sm.OLS(b[ind], c[ind])

    # DEBUG
    # print ma.fit().resid, mb.fit().resid
    # plt.scatter(ma.fit().resid, mb.fit().resid)
    #plt.scatter(a[ind], c[ind])
    #plt.show()

    return np.ma.corrcoef(ma.fit().resid, mb.fit().resid)[0,1]

def ztest(cc_con, cc_targ, n_con, n_targ):
    z_cc_con = np.arctanh(cc_con)
    z_cc_targ = np.arctanh(cc_targ)
    z_obs = (z_cc_con - z_cc_targ) / np.sqrt(1.0/(n_con - 3) + 1.0/(n_targ - 3))
    p_z = norm.sf(np.abs(z_obs))

    return z_obs, p_z
#====================================== PHYSIOLOGY ==============================================================
def cell_filter(dr, pfsfile, mincoh, maxspars, sresp, sel, minpfr, maxpfr):
    fpfs = open(dr + '/' + pfsfile)
    pfs = []
    for line in fpfs:
        pfs.append(line_to_floats(line))
    pfs = np.array(pfs)

    spars1 = np.array(read_float_list(dr + '/sparsity_BS6_OT5_E1.txt'))
    spars2 = np.array(read_float_list(dr + '/sparsity_BS6_OT5_E2.txt'))
    coh1 = np.array(read_float_list(dr + '/coherence_BS6_OT5_E1.txt'))
    coh2 = np.array(read_float_list(dr + '/coherence_BS6_OT5_E2.txt'))
    spars1nl = np.array(read_float_list(dr + '/sparsity_BS6_OT5_E1_NL1.txt'))
    spars2nl = np.array(read_float_list(dr + '/sparsity_BS6_OT5_E2_NL1.txt'))
    coh1nl = np.array(read_float_list(dr + '/coherence_BS6_OT5_E1_NL1.txt'))
    coh2nl = np.array(read_float_list(dr + '/coherence_BS6_OT5_E2_NL1.txt'))
    
    aresp = pfs[:,7]
    
    # RESPONSE filter :
    #       -  : no filtering
    #       a- : abs less
    #       a : abs more
    #       - <positive number> : less than <positive number>
    #       <positive value> : more than <positive value>
    if sresp == '0':
            indresp = np.array([True] * len(aresp))
            resp = 0
    else:
        if sresp[0] == 'a':
            if sresp[1] == '-':
                resp = float(sresp[2:])
                indresp = np.abs(aresp) < resp
            else:
                resp = float(sresp[1:])
                indresp = np.abs(aresp) > resp
        elif sresp[0] == '-':
            resp = float(sresp)
            indresp = aresp < resp
        else:
            resp = float(sresp)
            indresp = aresp > resp

    ind1 = ((spars1 < maxspars)  & (coh1 > mincoh) | (spars1nl < maxspars) & (coh1nl > mincoh)) & (pfs[:,8] > minpfr) & (pfs[:,8] < maxpfr) & indresp & ((pfs[:,8] > sel * pfs[:,9]) | np.isnan(pfs[:,9]))
    ind2 = ((spars2 < maxspars)  & (coh2 > mincoh) | (spars2nl < maxspars) & (coh2nl > mincoh)) & (pfs[:,9] > minpfr) & (pfs[:,9] < maxpfr) & indresp & ((pfs[:,9] > sel * pfs[:,8]) | np.isnan(pfs[:,8]))

    return ind1, ind2

# a provided rates array has peak rates in first two columns - in the env 1 / env 2
# pfspath2 - containing rates
# returns CONTROL, TARGET
def cell_filter_rates(dr, rates, mincoh, maxspars, sresp, respfile, sel, minpfr, maxpfr, pfspath, maxpfs, pfspath2):
    spars1 = np.array(read_float_list(dr + '/sparsity_BS6_OT5_E1.txt'))
    spars2 = np.array(read_float_list(dr + '/sparsity_BS6_OT5_E2.txt'))
    coh1 = np.array(read_float_list(dr + '/coherence_BS6_OT5_E1.txt'))
    coh2 = np.array(read_float_list(dr + '/coherence_BS6_OT5_E2.txt'))
    spars1nl = np.array(read_float_list(dr + '/sparsity_BS6_OT5_E1_NL1.txt'))
    spars2nl = np.array(read_float_list(dr + '/sparsity_BS6_OT5_E2_NL1.txt'))
    coh1nl = np.array(read_float_list(dr + '/coherence_BS6_OT5_E1_NL1.txt'))
    coh2nl = np.array(read_float_list(dr + '/coherence_BS6_OT5_E2_NL1.txt'))
    
    aresp = read_float_array(dr + '/' + respfile)

    wd = os.getcwd()
    os.chdir(dr)
    swap = int(resolve_vars(['%{swap}'])[0])
    #print swap
    os.chdir(wd)

    fpfs = open(dr + '/' + pfspath)
    pfs = []
    for line in fpfs:
        pfs.append(line_to_floats(line))
    pfs = np.array(pfs)
    
    fpfs2 = open(dr + '/' + pfspath2)
    pfs2 = []
    for line in fpfs2:
        pfs2.append(line_to_floats(line))
    pfs2 = np.array(pfs2)

    # RESPONSE filter :
    #       -  : no filtering
    #       a- : abs less
    #       a : abs more
    #       - <positive number> : less than <positive number>
    #       <positive value> : more than <positive value>
    if sresp == '0':
        indresp = np.array([True] * len(aresp))
        resp = 0
    elif ';' in sresp:
        cp = sresp.find(';')
        minr = float(sresp[:cp])
        maxr = float(sresp[cp+1:])
        #print 'Min, max responses: %.2f / %.2f' % (minr, maxr)
        print('WARNING: INVERSED RESPONSE FILTER FOR UNAFFECTED => UNAFFECTED EXCLUDED!')
        indresp = (aresp > minr) & (aresp < maxr)
        #indresp = (aresp < minr) | (aresp < maxr)
    else:
        if sresp[0] == 'a':
            if sresp[1] == '-':
                resp = float(sresp[2:])
                indresp = np.abs(aresp) < resp
            else:
                resp = float(sresp[1:])
                indresp = np.abs(aresp) > resp
        elif sresp[0] == '-':
            resp = float(sresp)
            indresp = aresp < resp
        else:
            resp = float(sresp)
            indresp = aresp > resp

    # E1, E2, ! not CON/TARG

    # MAX RATES
    #indr1 = (rates[:,1-swap] > minpfr) & (rates[:,1-swap] < maxpfr)
    #indr2 =  (rates[:,swap] > minpfr) & (rates[:,swap] < maxpfr)

    # MEAN RATES - IN 2nd PFS FILE - session 1 columns 8(e1) and 9(e2)
    indr1 = (pfs2[:,8] > minpfr) & (pfs2[:,8] < maxpfr)
    indr2 = (pfs2[:,9] > minpfr) & (pfs2[:,9] < maxpfr)

    # MAX RATES
    #sel1 = (rates[:,1-swap] > sel * rates[:,swap])
    #sel2 = (rates[:,swap] > sel * rates[:,1-swap])
    #sel1 = np.array([True] * len(aresp))
    #sel2 = np.array([True] * len(aresp))
    sel1 = np.isnan(pfs2[:,9]) | (pfs2[:,8] > sel * pfs2[:,9])
    sel2 = np.isnan(pfs2[:,8]) | (pfs2[:,9] > sel * pfs2[:,8])

    # ! NO SEL FILT !
    # pfs[:, 2 - swap], pfs[:, 1 + swap]
    ind1 = ((spars1 < maxspars)  & (coh1 > mincoh) | (spars1nl < maxspars) & (coh1nl > mincoh)) & indr1 & indresp & sel1 & (pfs[:,1] < maxpfs)
    ind2 = ((spars2 < maxspars)  & (coh2 > mincoh) | (spars2nl < maxspars) & (coh2nl > mincoh)) & indr2 & indresp & sel2 & (pfs[:,2] < maxpfs)

    # in the order of control / target
    if swap:
        return ind1, ind2
    else:
        return ind2, ind1
