all: liblapack.a magma-2.4.0/lib/libmagma.a

liblapack.a: ../lapack/lapack-3.8.0/liblapack.a

../lapack/lapack-3.8.0/liblapack.a:
	make -C ../lapack

magma-2.4.0.tar.gz:
	wget http://icl.utk.edu/projectsfiles/magma/downloads/magma-2.4.0.tar.gz

magma-2.4.0/make.inc: magma-2.4.0.tar.gz
	tar zxf magma-2.4.0.tar.gz
	cp make.inc magma-2.4.0

magma-2.4.0/lib/libmagma.a: magma-2.4.0/make.inc
	make -C magma-2.4.0 lib/libmagma.a
