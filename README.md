# SciPy-GPU

SciPy-GPU aims at being a drop-in replacement for some SciPy functions that run on the GPU.

## Install

You will need to have `scipy` and `gfortran` installed. The recommended way is to use `conda`:

```bash
conda install scipy
conda install gfortran_linux-64
```

Set some environment variables:

- `CONDADIR`: path to your Anaconda install, e.g. `/home/david/anaconda3`
- `GFORTRANDIR`: path to your `gfortran` install, e.g. `$CONDADIR/pkgs/gcc-4.8.5-7`
- `CUDADIR`: path to your CUDA install, e.g. `/usr/local/cuda-9.2`

And change the following paths according to the package versions you have installed:

```bash
$ export LD_LIBRARY_PATH=$CUDADIR/lib64:$CONDADIR/pkgs/libgcc-ng-7.2.0-hdf63c60_3/lib:$GFORTRANDIR/lib:$CONDADIR/pkgs/cloog-0.18.0-0/lib:$CONDADIR/pkgs/isl-0.12.2-0/lib:$LD_LIBRARY_PATH
```

You should create a virtual environment in order to prevent linking with the LAPACK library which may ship with Anaconda's distribution.

Then install with:

```bash
$ make -C f2py
```

You should now have some LAPACK functions executing through the MAGMA library.

```python
import numpy as np
import _flapack as mm               # MAGMA
import scipy.linalg.lapack as lp    # LAPACK
from time import time

m = 8192
n = 100
a = np.random.uniform(size=m*m).astype(np.float32, order='F').reshape((m, m))
b = np.random.uniform(size=m*n).astype(np.float32, order='F').reshape((m, n))

# sgesv solves a system of linear equations a*x=b
# see https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lapack.sgesv.html

t0 = time()
mm.sgesv(a, b)
t1 = time()
print('GPU time:', t1 - t0)

t0 = time()
lp.sgesv(a, b)
t1 = time()
print('CPU time:', t1 - t0)

# GPU time: 1.9766342639923096
# CPU time: 5.190711736679077
```
