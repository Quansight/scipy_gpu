python setup.py build
cp build/src.linux-x86_64-3.6/flapack.pyf .
cp build/src.linux-x86_64-3.6/flapack.pyf ../magma
python pyf2magma.py
cp gesv_to_magma_gesv_gpu.c ../magma
