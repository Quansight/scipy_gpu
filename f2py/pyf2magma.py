from numpy.f2py.crackfortran import crackfortran
import os
from pprint import pprint

def get_magma_types(magma_src, fname):
    with open(f'{magma_src}/{fname}.cpp') as f:
        txt = f.read()
    i0 = txt.find(f'magma_{fname}')
    i0 = txt[i0:].find('(') + i0 + 1
    i1 = txt[i0:].find(')') + i0
    params = txt[i0:i1].split(',')
    types = []
    names = []
    for param in params:
        p = param.split()
        t = p[0]
        n = p[1]
        if t == 'magma_int_t':
            t = 'int'
        elif t == 'magmaFloat_ptr':
            t = 'float*'
        elif t == 'magmaDouble_ptr':
            t = 'double*'
        if n.startswith('*'):
            t += '*'
            n = n[1:]
        types.append(t)
        names.append(n)
    return types, names

def pyf2magma(fin, fout, magma_src, ignore_func=[]):
    blocks = crackfortran([fin])
    if magma_src:
        magma_impl = [f[:-4] for f in os.listdir(magma_src) if f.endswith('.cpp')]
    else:
        magma_impl = []

    cfile = []
    cfile.append('#include <cuda.h>')
    cfile.append('#include "magma_v2.h"')
    cfile.append('#ifdef SCIPY_GPU_DEBUG')
    cfile.append('#include <stdio.h>')
    cfile.append('#endif')
    cfile.append('typedef struct {float r,i;} complex_float;')
    cfile.append('typedef struct {double r,i;} complex_double;')
    gpu_func = []
    for func in blocks[0]['body'][0]['body']:
        #pprint(func)
        name = func['name']
        ignore = False
        for func_name in ignore_func:
            startswith = False
            endswith = False
            if func_name[0] == '*':
                endsswith = True
                func_name = func_name[1:]
            if func_name[-1] == '*':
                startswith = True
                func_name = func_name[:-1]
            if startswith:
                if name.startswith(func_name):
                    ignore = True
            if endswith:
                if name.endswith(func_name):
                    ignore = True
            if name == func_name:
                ignore = True
        if name not in magma_impl:
            ignore = True
        if not ignore:
            types = func['f2pyenhancements']['callprotoargument'].split(',')
            magma_types, params = get_magma_types(magma_src, name)
            if len(types) != len(magma_types):
                # not the same number of parameters, ignore this function
                ignore = True
        if not ignore:
            gpu_func.append(name)
            cwrap = []
            proto = []
            proto.append(f'void {name}_(')
            proto.append(', '.join([f'{t} {p}' for t, p in zip(types, params)]))
            proto.append(') {')
            cwrap.append(''.join(proto))
            cwrap.append('#ifdef SCIPY_GPU_DEBUG')
            cwrap.append(f'    fprintf(stderr, "GPU {name}\\n");')
            cwrap.append('#endif')
            cwrap.append('    magma_init();')
            # MAGMA function call
            margs = []
            for p, t, mt in zip(params, types, magma_types):
                if t == mt:
                    ma = p
                else:
                    ma = f'*{p}'
                margs.append(ma)
            margs = ', '.join(margs)
            cwrap.append(f'    magma_{name}({margs});')
            cwrap.append('    magma_finalize;')
            cwrap.append('}')
            cwrap = '\n'.join(cwrap)
            cfile.append(cwrap)
    
    with open(f'{fout}.c', 'wt') as f:
        f.write('\n'.join(cfile))

    with open(f'{fout}.sh', 'wt') as f:
        txt = 'ar dv liblapack.a'
        for func in gpu_func:
            txt += f' {func}.o'
        f.write(txt)

if __name__ == '__main__':
    cfname = 'lapack_to_magma'
    pyf2magma('flapack.pyf', cfname, '../magma/magma-2.4.0/src', ignore_func=['c*', 'z*'])
    print(f'Wrote file {cfname}')
