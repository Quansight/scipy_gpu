all: lapack-3.8.0/liblapack.a lapack-3.8.0/librefblas.a xblas-1.0.248/libxblas.a

test: test_lapack.py lapackmodule.c lapack-3.8.0/liblapack.a lapack-3.8.0/librefblas.a xblas-1.0.248/libxblas.a
	f2py -c lapack.pyf -llapack -lrefblas -lxblas -lgfortran -Llapack-3.8.0 -Lxblas-1.0.248
	python test_lapack.py

lapackmodule.c: lapack-3.8.0/make.inc lapack.pyf
	f2py -m lapack lapack-3.8.0/SRC/dgesv.f -h lapack.pyf

lapack-3.8.0.tar.gz:
	wget http://www.netlib.org/lapack/lapack-3.8.0.tar.gz

lapack-3.8.0/make.inc: lapack-3.8.0.tar.gz
	tar zxf lapack-3.8.0.tar.gz
	cp make.inc.lapack lapack-3.8.0/make.inc

lapack-3.8.0/liblapack.a: lapack-3.8.0/make.inc
	make -C lapack-3.8.0 lapacklib

lapack-3.8.0/librefblas.a: lapack-3.8.0/make.inc
	make -C lapack-3.8.0 blaslib

xblas.tar.gz:
	wget http://www.netlib.org/xblas/xblas.tar.gz

xblas-1.0.248/make.inc: xblas.tar.gz
	tar zxf xblas.tar.gz
	cp make.inc.xblas xblas-1.0.248/make.inc

xblas-1.0.248/libxblas.a: xblas-1.0.248/make.inc
	make -C xblas-1.0.248 lib

clean:
	rm -f lapack-3.8.0/liblapack.a lapack-3.8.0/librefblas.a xblas-1.0.248/libxblas.a
