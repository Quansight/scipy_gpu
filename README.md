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

Then install with (set `SCIPY_GPU_DEBUG` for debug information during run):

```bash
$ SCIPY_GPU_DEBUG=1 make -C magma
```

You should now have some LAPACK functions executing through the MAGMA library. You should create a virtual environment in order to prevent linking with the LAPACK library which may ship with the Anaconda's distribution.

```python
import numpy as np
import _flapack as lp

# Solve a system of linear equations A*x=b
A = np.array([[1, 2], [3, 4]])
b = np.array([[5], [6]], dtype=np.float64, order='F')
print(lp.dgesv(A, b))
# see https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.linalg.lapack.dgesv.html
# x should be:
# array([[-4. ],
#        [ 4.5]])
```
