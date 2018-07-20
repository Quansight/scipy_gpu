import os

magma_files = [f[:-8] for f in os.listdir('../magma/magma-2.4.0/src') if f.endswith('_gpu.cpp')]
lapack_files = [f[:-2] for f in os.listdir('lapack-3.8.0/SRC') if f.endswith('.f')]

for f in magma_files:
    if f in lapack_files:
        print(f)
