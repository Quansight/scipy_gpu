all: lapack_to_magma.c
	cp flapack.pyf ../magma
	cp lapack_to_magma.c ../magma
	cp lapack_to_magma.c.func ../magma

flapack.pyf: setup.py
	python setup.py build_src
	cp build/src.linux-x86_64-3.6/flapack.pyf .

../magma/magma-2.4.0/make.inc:
	make -C ../magma magma-2.4.0/make.inc

lapack_to_magma.c: flapack.pyf ../magma/magma-2.4.0/make.inc
	python pyf2magma.py

clean:
	rm -rf build flapack.pyf lapack_to_magma.c
