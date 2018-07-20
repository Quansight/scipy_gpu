wget http://www.netlib.org/lapack/lapack-3.8.0.tar.gz
tar zxf lapack-3.8.0.tar.gz
cp make.inc.lapack lapack-3.8.0/make.inc

wget http://www.netlib.org/xblas/xblas.tar.gz
tar zxf xblas.tar.gz
cp make.inc.xblas xblas-1.0.248/make.inc

cd lapack-3.8.0
make blaslib
make lapacklib
cd ..

cd xblas-1.0.248
make lib
cd ..

f2py -m lapack lapack-3.8.0/SRC/dgesv.f -h lapack.pyf
f2py -c lapack.pyf -llapack -lrefblas -lxblas -lgfortran -Llapack-3.8.0 -Lxblas-1.0.248
python test_lapack.py
