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
