all: flapack.pyf ../lapack/lapack-3.8.0/liblapack.a ../lapack/lapack-3.8.0/librefblas.a ../lapack/xblas-1.0.248/libxblas.a liblapack_to_magma.a magma-2.4.0/lib/libmagma.a
	f2py -c flapack.pyf -lgomp -llapack_to_magma -lmagma -llapack -lrefblas -lxblas -lgfortran -lcudart -lcublas -lcusparse -L$(PWD) -L/usr/lib/x86_64-linux-gnu -L$(PWD)/../lapack/lapack-3.8.0 -L$(PWD)/../lapack/xblas-1.0.248 -L$(PWD)/magma-2.4.0/lib

../lapack/lapack-3.8.0/liblapack.a ../lapack/lapack-3.8.0/librefblas.a ../lapack/xblas-1.0.248/libxblas.a:
	make -C ../lapack

flapack.pyf lapack_to_magma.c:
	make -C ../f2py

magma-2.4.0.tar.gz:
	wget http://icl.utk.edu/projectsfiles/magma/downloads/magma-2.4.0.tar.gz

magma-2.4.0/make.inc: magma-2.4.0.tar.gz
	tar zxf magma-2.4.0.tar.gz
	cp make.inc magma-2.4.0

magma-2.4.0/lib/libmagma.a: magma-2.4.0/make.inc
	make -C magma-2.4.0 lib

lapack_to_magma.o: lapack_to_magma.c magma-2.4.0/make.inc
	gcc -fopenmp -c lapack_to_magma.c -Imagma-2.4.0/include -fPIC

liblapack_to_magma.a: lapack_to_magma.o
	ar rcs liblapack_to_magma.a lapack_to_magma.o

clean:
	rm -f *.a *.o *.so lapack_to_magma.c flapack.pyf
