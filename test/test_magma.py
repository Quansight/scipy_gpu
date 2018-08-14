import numpy as np
from pandas import DataFrame
import _flapack as mm               # MAGMA
import scipy.linalg.lapack as lp    # LAPACK
from time import time

def get_dtype(funcname):
    if funcname.startswith('s'):
        dtype = np.float32
    elif funcname.startswith('d'):
        dtype = np.float64
    return dtype

def get_time(funcname, args, df, keep_result=False):
    print(funcname)
    df[funcname] = {}
    for target, module in {'gpu': mm, 'cpu': lp}.items():
        func = module.__getattribute__(funcname)
        t0 = time()
        ret = func(*args)
        t1 = time()
        t = t1 - t0
        df[funcname][target] = t
        if keep_result:
            df[funcname]['ret'] = ret
        print(target, t)
    print()

df = {}

################################################################################

func = 'gesv'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    m = 8192
    n = 100
    a = np.random.uniform(size=m*m).astype(dtype, order='F').reshape((m, m))
    b = np.random.uniform(size=m*n).astype(dtype, order='F').reshape((m, n))
    
    get_time(funcname, (a, b), df)

################################################################################

func = 'getrf'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    m = 8192
    n = 8192
    a = np.random.uniform(size=m*n).astype(dtype, order='F').reshape((m, n))
    
    get_time(funcname, (a, ), df, keep_result=True)

################################################################################

func = 'getrs'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    n = 8192
    nrhs = 100
    b = np.ones((m, nrhs), dtype=dtype, order='F')
    lu, piv, info = df[prefix + 'getrf']['ret']
    
    get_time(funcname, (lu, piv, b), df)

################################################################################

func = 'getri'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    lu, piv, info = df[prefix + 'getrf']['ret']
    
    get_time(funcname, (lu, piv), df)



################################################################################

index = list(df.keys())
gpu_time = [df[func]['gpu'] for func in df]
cpu_time = [df[func]['cpu'] for func in df]
df = DataFrame({'GPU': gpu_time, 'CPU': cpu_time}, index=index)
df = (1 / df).replace(np.inf ,0)
df = df.div(df.max(axis=1), axis=0)
df.to_pickle('benchmark.pkl')
ax = df.plot.bar(title='Speed (1 is fastest)', figsize=(15, 5))
fig = ax.get_figure()
fig.savefig('benchmark.png', bbox_inches='tight')
