import numpy as np
import _flapack as mm
import scipy.linalg.lapack as lp
from time import time

m = 8192
n = 100
a = np.random.uniform(size=m*m).astype(np.float64, order='F').reshape((m, m))
b = np.random.uniform(size=m*n).astype(np.float64, order='F').reshape((m, n))

t0 = time()
mm.dgesv(a, b)
t1 = time()
print('GPU time:', t1 - t0)

t0 = time()
lp.dgesv(a, b)
t1 = time()
print('CPU time:', t1 - t0)
