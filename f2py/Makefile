all: ../magma-2.4.0/lib/libmagma.a test/lapack.cpython-36m-x86_64-linux-gnu.so

../magma-2.4.0/lib/libmagma.a:
	make -C ../magma

test/lapack.cpython-36m-x86_64-linux-gnu.so: setup.py flapack_gen.pyf.src
	python setup.py build_src
	python to_magma.py build/src.linux-x86_64-3.6/build/src.linux-x86_64-3.6/_flapackmodule.c
	python setup.py build
	cp build/lib.linux-x86_64-3.6/linalg/_flapack.cpython-36m-x86_64-linux-gnu.so ../test/magma.cpython-36m-x86_64-linux-gnu.so

clean:
	rm -rf build
