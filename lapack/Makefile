all: lapack-3.8.0/liblapack.a lapack-3.8.0/librefblas.a

test: test_lapack.py lapackmodule.c lapack-3.8.0/liblapack.a lapack-3.8.0/librefblas.a
	f2py -c lapack.pyf -llapack -lrefblas -lgfortran -Llapack-3.8.0 -L$(GFORTRANDIR)/lib
	python test_lapack.py

lapackmodule.c: lapack-3.8.0/make.inc lapack.pyf
	f2py -m lapack lapack-3.8.0/SRC/dgesv.f -h lapack.pyf

lapack-3.8.0.tar.gz:
	wget http://www.netlib.org/lapack/lapack-3.8.0.tar.gz

lapack-3.8.0/make.inc: lapack-3.8.0.tar.gz
	tar zxf lapack-3.8.0.tar.gz
	cp make.inc lapack-3.8.0

lapack-3.8.0/liblapack.a: lapack-3.8.0/make.inc
	make -C lapack-3.8.0 lapacklib

lapack-3.8.0/librefblas.a: lapack-3.8.0/make.inc
	make -C lapack-3.8.0 blaslib

clean:
	rm -f lapack-3.8.0/*.a *.so
