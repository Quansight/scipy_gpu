import os
from numpy.f2py.crackfortran import crackfortran

def get_types(saved_interface):
    lines = saved_interface.splitlines()
    lines = [l.strip() for l in lines]
    lines = [l[:l.find(',')] for l in lines if l and not l.startswith(('subroutine', 'end', 'call', 'threadsaf'))]
    conv = {'integer': 'int*', 'character': 'char*', 'real': 'float*', 'double precision': 'double*'}
    return [conv[l] for l in lines]

def get_magma_types(magma_src, fname):
    with open(f'{magma_src}/{fname}.cpp') as f:
        txt = f.read()
    i0 = txt.find(f'magma_{fname}')
    i0 = txt[i0:].find('(') + i0 + 1
    i1 = txt[i0:].find(')') + i0
    params = txt[i0:i1].split(',')
    types = []
    names = []
    convs = []
    for param in params:
        p = param.split()
        t = p[0]
        n = p[1]
        c = ''
        if t == 'magma_int_t':
            t = 'int'
        elif t == 'magmaFloat_ptr':
            t = 'float*'
        elif t == 'magmaDouble_ptr':
            t = 'double*'
        elif t == 'magma_uplo_t':
            t = 'char'
            v = f'_magma_{n}_'
            c = f"magma_uplo_t {v}; switch (*{n}) {{ case 'U': {v} = MagmaUpper; break; case 'L': {v} = MagmaLower; break; default: fprintf(stderr, \"magma_uplo_t doesn't map all LAPACK possible character values.\"); exit(EXIT_FAILURE); break; }}"
        elif t == 'magma_trans_t':
            t = 'char'
            v = f'_magma_{n}_'
            c = f"magma_trans_t {v}; switch (*{n}) {{ case 'N': {v} = MagmaNoTrans; break; case 'T': {v} = MagmaTrans; break; default: fprintf(stderr, \"magma_trans_t doesn't map all LAPACK possible character values.\"); exit(EXIT_FAILURE); break; }}"
        elif t == 'magma_vec_t':
            t = 'char'
            v = f'_magma_{n}_'
            c = f"magma_vec_t {v}; switch (*{n}) {{ case 'N': {v} = MagmaNoVec; break; case 'V': {v} = MagmaVec; break; case 'O': {v} = MagmaOverwriteVec; break; case 'A': {v} = MagmaAllVec; break; case 'S': {v} = MagmaSomeVec; break; default: fprintf(stderr, \"magma_vec_t doesn't map all LAPACK possible character values.\"); exit(EXIT_FAILURE); break; }}"
        if n.startswith('*'):
            t += '*'
            n = n[1:]
        types.append(t)
        names.append(n)
        convs.append(c)
    return types, names, convs

def to_magma(fin, module, magma_src, ignore_func=[]):
    if magma_src:
        magma_impl = [f[:-4] for f in os.listdir(magma_src) if f.endswith('.cpp')]
    else:
        magma_impl = []

    ignores = []
    blocks = crackfortran([fin])
    cfile = []
    cfile.append('#include <cuda.h>')
    cfile.append('#include "magma_v2.h"')
    cfile.append('#include <stdio.h>')
    cfile.append('#include <stdlib.h>')
    cfile.append('typedef struct {float r,i;} complex_float;')
    cfile.append('typedef struct {double r,i;} complex_double;')
    for func in blocks[0]['body'][0]['body']:
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
                    print(f'{name} ignored because starts with {func_name}')
            if endswith:
                if name.endswith(func_name):
                    ignore = True
                    print(f'{name} ignored because ends with {func_name}')
            if name == func_name:
                ignore = True
                print(f'{name} ignored because equals {func_name}')
        if name not in magma_impl:
            ignore = True
            print(f'{name} ignored because not found in MAGMA')
        if not ignore:
            if 'f2pyenhancements' in func:
                types = func['f2pyenhancements']['callprotoargument'].split(',')
            else:
                types = get_types(func['saved_interface'])
            magma_types, params, convs = get_magma_types(magma_src, name)
            if len(types) != len(magma_types):
                # not the same number of parameters, ignore this function
                ignore = True
                print(f'{name} ignored because parameters between LAPACK and MAGMA mismatch')
        if ignore:
            ignores.append(name)
        else:
            cwrap = []
            proto = []
            proto.append(f'void _magma_{name}(')
            proto.append(', '.join([f'{t} {p}' for t, p in zip(types, params)]))
            proto.append(') {')
            cwrap.append(''.join(proto))
            cwrap.append('#ifdef SCIPY_GPU_DEBUG')
            cwrap.append(f'    fprintf(stderr, "GPU {name}\\n");')
            for p, t in zip(params, types):
                pt = {'char*': 'c', 'int*': 'd'}.get(t, None)
                if pt:
                    cwrap.append(f'    fprintf(stderr, "{p}=%{pt}\\n", *{p});')
            cwrap.append('#endif')
            # MAGMA function call
            margs = []
            for p, t, mt, c in zip(params, types, magma_types, convs):
                if c:
                    ma = f'_magma_{p}_'
                    cwrap.append(f'    {c}')
                elif t == mt:
                    ma = p
                else:
                    ma = f'*{p}'
                margs.append(ma)
            margs = ', '.join(margs)
            cwrap.append(f'    magma_{name}({margs});')
            cwrap.append('}')
            cwrap = '\n'.join(cwrap)
            cfile.append(cwrap)
    
    with open(f'to_magma.c', 'wt') as f:
        f.write('\n'.join(cfile))

    with open(module) as f:
        clines = f.readlines()
    
    new_clines = []
    first_extern = True
    s0 = 'extern void F_FUNC('
    s1 = 'F_FUNC('
    for l in clines:
        line_done = False
        if not line_done:
            if (s0 in l) and not l.startswith('/*'):
                if first_extern:
                    first_extern = False
                    new_clines.append('extern void magma_init();\n')
                    new_clines.append('extern void magma_finalize();\n')
                i0 = l.find(s0) + len(s0)
                i1 = l.find(',')
                name = l[i0:i1]
                i2 = l.find(')')
                if name not in ignores:
                    line_done = True
                    new_l = f'extern void _magma_{name}' + l[i2+1:]
                    new_clines.append(new_l)
        if not line_done:
            if (s1 in l) and ('f2py_init_func') in l:
                i0 = l.find(s1)
                i1 = i0 + len(s1)
                i2 = l[i1:].find(',') + i1
                name = l[i1:i2]
                i3 = l[i1:].find(')') + i1
                if name not in ignores:
                    line_done = True
                    new_l = l[:i0] + f'_magma_{name}' + l[i3+1:]
                    new_clines.append(new_l)
        if not line_done:
            new_clines.append(l)

    i = len(new_clines)
    done = False
    while not done:
        i -= 1
        if 'return RETVAL;' in new_clines[i]:
            new_clines.insert(i, '  magma_init();\n')
            new_clines.insert(i, '  on_exit(magma_finalize,(void*)"_flapack");\n')
            done = True
    
    with open(module, 'wt') as f:
        f.write(''.join(new_clines))

if __name__ == '__main__':
    to_magma('build/src.linux-x86_64-3.6/flapack.pyf', 'build/src.linux-x86_64-3.6/build/src.linux-x86_64-3.6/_flapackmodule.c', '../magma/magma-2.4.0/src', ignore_func=['c*', 'z*'])
