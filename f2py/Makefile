all: lapack_to_magma.c
	cp flapack.pyf ../magma
	cp lapack_to_magma.c ../magma

flapack.pyf: setup.py
	python setup.py build_src
	cp build/src.linux-x86_64-3.6/flapack.pyf .

lapack_to_magma.c: flapack.pyf
	python pyf2magma.py

clean:
	rm -rf build flapack.pyf lapack_to_magma.c
