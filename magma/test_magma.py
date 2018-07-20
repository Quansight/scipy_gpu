import numpy as np
import lapack as lp

# Solve a system of linear equations A*x=b
A = np.array([[1, 2], [3, 4]])
b = np.array([[5], [6]], dtype=np.float64, order='F')
lp.dgesv(2, 1, A, [0, 0], b, 0)
print(b)
# array([[-4. ],
#        [ 4.5]])
