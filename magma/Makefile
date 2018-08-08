all: flapack.pyf ../lapack/lapack-3.8.0/liblapack.a ../lapack/lapack-3.8.0/librefblas.a liblapack_to_magma.a magma-2.4.0/lib/libmagma.a
	f2py -c flapack.pyf --f90flags='-fopenmp' -lgomp -llapack_to_magma -lmagma -llapack -lrefblas -lgfortran -lcudart -lcublas -lcusparse -L. -L$(GFORTRANDIR)/lib -L$(CUDADIR)/lib64 -L../lapack/lapack-3.8.0 -Lmagma-2.4.0/lib

../lapack/lapack-3.8.0/liblapack.a ../lapack/lapack-3.8.0/librefblas.a: lapack_to_magma.c
	make -C ../lapack
	cd ../lapack/lapack-3.8.0; bash ../../magma/lapack_to_magma.sh

flapack.pyf lapack_to_magma.c:
	make -C ../f2py

magma-2.4.0.tar.gz:
	wget http://icl.utk.edu/projectsfiles/magma/downloads/magma-2.4.0.tar.gz

magma-2.4.0/make.inc: magma-2.4.0.tar.gz
	tar zxf magma-2.4.0.tar.gz
	cp make.inc magma-2.4.0

magma-2.4.0/lib/libmagma.a: magma-2.4.0/make.inc
	make -C magma-2.4.0 lib/libmagma.a

lapack_to_magma.o: lapack_to_magma.c magma-2.4.0/make.inc
	gcc -fopenmp -c lapack_to_magma.c -Imagma-2.4.0/include -I$(CUDADIR)/include -D$(SCIPY_GPU_DEBUG) -fPIC

liblapack_to_magma.a: lapack_to_magma.o
	ar rcs liblapack_to_magma.a lapack_to_magma.o

clean:
	rm -f *.a *.o *.so lapack_to_magma.c flapack.pyf
