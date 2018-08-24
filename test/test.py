import numpy as np
from pandas import DataFrame
import _flapack as mm               # MAGMA
import scipy.linalg.lapack as lp    # LAPACK
import scipy.linalg.blas as bl      # BLAS
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
            # keep the CPU result
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
    a = np.random.uniform(size=m*m).reshape((m, m)).astype(dtype, order='F')
    b = np.random.uniform(size=m*n).reshape((m, n)).astype(dtype, order='F')
    
    get_time(funcname, (a, b), df)

################################################################################

func = 'getrf'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    m = 8192
    n = 8192
    a = np.random.uniform(size=m*n).reshape((m, n)).astype(dtype, order='F')
    
    get_time(funcname, (a, ), df, keep_result=True)

################################################################################

func = 'getrs'

for prefix in []:#['s', 'd']: # not executed on the GPU
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    n = 8192
    nrhs = 100
    b = np.ones((m, nrhs), dtype=dtype, order='F')
    lu, piv, info = df[prefix + 'getrf']['ret']
    
    get_time(funcname, (lu, piv, b), df)

################################################################################

func = 'getri'

for prefix in []:#['s', 'd']: # not executed on the GPU
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    lu, piv, info = df[prefix + 'getrf']['ret']
    
    get_time(funcname, (lu, piv), df)

################################################################################

func = 'posv'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)

    m = 8192
    n = 100
    a = np.random.uniform(size=m*m).reshape((m, m)).astype(dtype, order='F')
    b = np.ones((m, n), dtype=dtype, order='F')
    alpha = 1.
    if dtype == np.float32:
        c = bl.sgemm(alpha, a, b)
    elif dtype == np.float64:
        c = bl.dgemm(alpha, a, b)

    get_time(funcname, (a, c), df)

################################################################################

func = 'potrf'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    m = 8192
    a = np.random.uniform(size=m*m).reshape((m, m)).astype(dtype, order='F')

    get_time(funcname, (a, ), df, keep_result=True)

################################################################################

func = 'potri'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    c, info = df[prefix + 'potrf']['ret']

    get_time(funcname, (c, ), df)

################################################################################

func = 'gels'

for prefix in []:#['s', 'd']: # illegal parameter value
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    m = 8192
    n = 8192
    nrhs = 100
    a = np.random.uniform(size=m*n).reshape((m, n)).astype(dtype, order='F')
    b = np.random.uniform(size=m*nrhs).reshape((m, nrhs)).astype(dtype, order='F')

    get_time(funcname, (a, b), df)

################################################################################

func = 'geqrf'

for prefix in []:#['s', 'd']: # illegal parameter value
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    m = 4096
    n = 4096
    a = np.random.uniform(size=m*n).reshape((m, n)).astype(dtype, order='F')

    get_time(funcname, (a, ), df)

################################################################################

func = 'geev'

for prefix in []:#['s', 'd']: # segmentation fault
    funcname = prefix + func
    dtype = get_dtype(funcname)
    
    n = 1024
    a = np.random.uniform(size=n*n).reshape((n, n)).astype(dtype, order='F')

    get_time(funcname, (a, ), df)

#################################################################################

func = 'gesvd'

for prefix in []:#['s', 'd']: # illegal parameter value
    funcname = prefix + func
    dtype = get_dtype(funcname)

    n = 8192
    a = np.random.uniform(size=n*n).reshape((n, n)).astype(dtype, order='F')

    get_time(funcname, (a, ), df)

#################################################################################

func = 'syevd'

for prefix in ['s', 'd']:
    funcname = prefix + func
    dtype = get_dtype(funcname)

    n = 1024
    a = np.random.uniform(size=n*n).reshape((n, n)).astype(dtype, order='F')

    get_time(funcname, (a, ), df)



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
