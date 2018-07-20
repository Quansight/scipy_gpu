wget http://icl.utk.edu/projectsfiles/magma/downloads/magma-2.4.0.tar.gz
tar zxf magma-2.4.0.tar.gz
cp make.inc magma-2.4.0
cd magma-2.4.0
make lib
make sparce-lib

cp ../lapack/lapack.pyf .
gcc -fopenmp -c dgesv_to_magma_dgesv_gpu.c -Imagma-2.4.0/include
cp magma-2.4.0/lib/libmagma.a .
rm -rf lapack_lib
mkdir lapack_lib
cd lapack_lib
ar -x ../../lapack/lapack-3.8.0/liblapack.a
rm dgesv.o
ar r ../libmagma.a *.o
rm *.o
cp ../dgesv_to_magma_dgesv_gpu.o .
cp ../magma-2.4.0/control/*.o .
cd ../magma-2.4.0/magmablas
for f in *.o; do cp -- "$f" "../../lapack_lib/magma_$f"; done
cd ../../lapack_lib
ar r ../libmagma.a *.o
rm *.o
cd ..
f2py -c lapack.pyf -lgomp -lmagma -lrefblas -lxblas -lgfortran -lcudart -lcublas -lcusparse -L. -L/usr/lib/x86_64-linux-gnu -L../lapack/lapack-3.8.0 -L../lapack/xblas-1.0.248
python test_magma.py
