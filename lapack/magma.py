import os

magma_files = [f[:-4] for f in os.listdir('../magma/magma-2.4.0/src') if f.endswith('.cpp') and not f.endswith('_gpu.cpp')]
lapack_files = [f[:-2] for f in os.listdir('lapack-3.8.0/SRC') if f.endswith('.f')]

common_functions = []
for f in magma_files:
    if f in lapack_files:
        f2 = f[1:]
        if f2 not in common_functions:
            common_functions.append(f2)
print(' '.join(common_functions))

# all functions present in LAPACK and MAGMA (CPU interface):

#geqp3
#hegvx          only available in c and z
#geev           segmentation fault
#lauum          available in flapack_other
#laqps          not in scipy.linalg.lapack
#gesvd          illegal parameter value
#sysv
#potrf
#gehrd          segmentation fault
#gels           illegal parameter value
#gesdd
#potri
#unmql          not in scipy.linalg.lapack
#unmtr          not in scipy.linalg.lapack
#sygst
#gebrd          not in scipy.linalg.lapack
#sytrd_sy2sb    not in scipy.linalg.lapack
#sygvd
#gglse          available in flapack_other
#hetrd_he2hb    not in scipy.linalg.lapack
#unmqr          only available in c and z
#sytrd          illegal parameter value
#hesv           only available in c and z
#sytrf
#geqrf          illegal parameter value
#ggrqf          not in scipy.linalg.lapack
#orghr          available in flapack_other
#posv
#laln2          not in scipy.linalg.lapack
#orgqr          available in flapack_other
#ormrq          not in scipy.linalg.lapack
#ormlq          not in scipy.linalg.lapack
#orglq          not in scipy.linalg.lapack
#lahr2          not in scipy.linalg.lapack
#orgbr          not in scipy.linalg.lapack
#ormbr          not in scipy.linalg.lapack
#gesv
#trevc3         not in scipy.linalg.lapack
#ungtr          not in scipy.linalg.lapack
#unglq          not in scipy.linalg.lapack
#heevx          not in scipy.linalg.lapack
#hetrd          only available in c and z
#ungbr          not in scipy.linalg.lapack
#geqlf          not in scipy.linalg.lapack
#getrf
#ormqr          available in flapack_other
#latrd          not in scipy.linalg.lapack
#unghr          only available in c and z
#hegst          only available in c and z
#syevd
#ungqr          only available in c and z
#trtri          available in flapack_other
#gelqf          not in scipy.linalg.lapack
#hetrf          only available in c and z
#heevd          only available in c and z
#hegvd          only available in c and z
#unmlq          not in scipy.linalg.lapack
#heevr          only available in c and z
#unmbr          not in scipy.linalg.lapack
#unmrq          not in scipy.linalg.lapack
#orgtr          not in scipy.linalg.lapack
#ormql          not in scipy.linalg.lapack
#ormtr          not in scipy.linalg.lapack
