ifeq ($(SCIPY_GPU_DEBUG),TRUE)
	DEFINE_SCIPY_GPU_DEBUG=-DSCIPY_GPU_DEBUG
else
	DEFINE_SCIPY_GPU_DEBUG=
endif

all: ../magma-2.4.0/lib/libmagma.a test/lapack.cpython-36m-x86_64-linux-gnu.so

../magma-2.4.0/lib/libmagma.a:
	make -C ../magma

test/lapack.cpython-36m-x86_64-linux-gnu.so: libto_magma.a
	python setup.py build
	cp build/lib.linux-x86_64-3.6/linalg/_flapack.cpython-36m-x86_64-linux-gnu.so ../test

build/src.linux-x86_64-3.6/build/src.linux-x86_64-3.6/_flapackmodule.c:
	python setup.py build_src

to_magma.c: build/src.linux-x86_64-3.6/build/src.linux-x86_64-3.6/_flapackmodule.c
	python to_magma.py

to_magma.o: to_magma.c
	gcc -c to_magma.c -I../magma/magma-2.4.0/include -I$(CUDADIR)/include $(DEFINE_SCIPY_GPU_DEBUG) -fPIC

libto_magma.a: to_magma.o
	ar rcs libto_magma.a to_magma.o

clean:
	rm -rf build *.a *.o
