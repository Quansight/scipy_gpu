from numpy.f2py.crackfortran import crackfortran
import os
from pprint import pprint

def get_magma_params(params):
    magma_params = []
    for p in params:
        mp = f'magma_{p}'
        while (mp in params) or (mp in magma_params):
            mp += '_'
        magma_params.append(mp)
    magma_params = {p: mp for p, mp in zip(params, magma_params)}
    return magma_params

def get_call_args(callstatement):
    # simple parser, might not be enough for complex expression arguments
    # TODO: better parser
    callstatement += ';'
    i0 = callstatement.find('f2py_func')
    i0 += callstatement[i0:].find('(') + 1
    i1 = callstatement[i0:].find(';') + i0
    i1 = callstatement[i0:i1].rfind(')') + i0
    args = callstatement[i0:i1].split(',')
    for i, a in enumerate(args):
        a = a.strip()
        a = a[a.startswith('&'):]
        lst = ['"', '?', ':', '(', ')', "'"]
        if any(s in a for s in lst):
            name = 'expression'
            while args.count(name) > 0:
                name = '_' + name
            args[i] = name
        else:
            args[i] = a
    return args

def get_lapack_args(fname, path):
    with open(os.path.join(path, fname + '.f')) as f:
        fcode = f.readlines()
    args = []
    for line in fcode:
        line = line.lstrip()
        look_for = 'SUBROUTINE'
        if line.startswith(look_for):
            line = line.lstrip(look_for)
            i0 = line.find('(')
            name = line[:i0].strip().lower()
            if name == fname:
                args = line
                break
    if args:
        i1 = args.find(')')
        args = [arg.strip().lower() for arg in args[i0+1:i1].split(',')]
    return args

def from_type(typespec):
    '''
    From the 'typespec' field, return the following tuple:
    (c_type, magma_type, magma_malloc, magma_setmatrix, magma_getmatrix)
    where:
    - c_type is the C type
    - magma_type is the MAGMA type
    - magma_malloc is the MAGMA malloc function
    - magma_setmatrix is the MAGMA setmatrix function
    - magma_getmatrix is the MAGMA getmatrix function
    '''
    if typespec == 'integer':
        return 'int', 'magma_int_t', '', '', ''
    if typespec == 'real':
        return 'float', 'float', 'magma_smalloc', 'magma_ssetmatrix', 'magma_sgetmatrix'
    if typespec == 'double precision':
        return 'double', 'double', 'magma_dmalloc', 'magma_dsetmatrix', 'magma_dgetmatrix'
    return 'unknown_type', 'unknown_type', '', '', ''

def pyf2magma(fin, fout, ignore_func=[], magma_src=''):
    blocks = crackfortran([fin])
    if magma_src:
        magma_impl = [f[:-8] for f in os.listdir(magma_src) if f.endswith('_gpu.cpp')]
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
    # function parameter names are inferred from calling arguments
    # when same argument is passed, corresponding parameter name is uniquified
    # `param_aliases` maps the uniquified parameters to the calling arguments
    param_aliases = {}
    gpu_func = []
    for func in blocks[0]['body'][0]['body']:
        #pprint(func)
        name = func['name']
        ignore = False
        for func_name in ignore_func:
            startswith = False
            if func_name.endswith('...'):
                startswith = True
                func_name = func_name[:-3]
            if startswith:
                if name.startswith(func_name):
                    ignore = True
            else:
                if name == func_name:
                    ignore = True
        if (not ignore) and (name in magma_impl):
            print(name)
            gpu_func.append(name)
            types = func['f2pyenhancements']['callprotoargument'].split(',')
            params = get_call_args(func['f2pyenhancements']['callstatement'])
            # duplicate arguments are uniquified by appending '_'
            for i in range(len(params)):
                is_alias = False
                p = params[i]
                n = 1
                while params.count(p) > n:
                    n = 0
                    p += '_'
                    is_alias = True
                if is_alias:
                    param_aliases[p] = params[i]
                params[i] = p
            magma_params = get_magma_params(params)

            #args = list(func['vars'].keys())
            #types = [from_type(func['vars'][a]['typespec']) for a in args]
            ## unused arguments are uniquified by appending '_'.
            ## supposes original arguments don't end with '_' !!!
            ## TODO: better uniquify
            #args = [a+'_'*(args[:i].count(a)) for i, a in enumerate(args)]
            
            cwrap = []
            proto = []
            #lapack_types = func['f2pyenhancements']['callprotoargument'].split(',')
            #lapack_args = get_lapack_args(name, '../lapack/lapack-3.8.0/SRC')

            #call_args = get_call_args(func['f2pyenhancements']['callstatement'])
            #wrapper_args = []
            #for la, ca in zip(lapack_args, call_args):
            #    if ca in args:
            #        arg = ca
            #        # same argument passed, ignore it by uniquifying it
            #        while arg in wrapper_args:
            #            arg += '_'
            #    else:
            #        arg = la
            #    wrapper_args.append(arg)

            proto.append(f'void {name}_(')
            proto.append(', '.join([f'{t} {p}' for t, p in zip(types, params)]))
            proto.append(') {')
            cwrap.append(''.join(proto))
            cwrap.append('#ifdef SCIPY_GPU_DEBUG')
            cwrap.append(f'    fprintf(stderr, "GPU {name}\\n");')
            cwrap.append('#endif')
            cwrap.append('    magma_init();')
            cwrap.append('    magma_queue_t queue = NULL;')
            cwrap.append('    magma_int_t dev = 0;')
            cwrap.append('    magma_queue_create(dev, &queue);')
            cwrap.append('    magma_int_t err;')
            # copy parameters to the GPU
            for t, p in zip(types, params):
                if p not in param_aliases:
                    # argument was not a duplicate
                    if p in func['vars']:
                        # argument was not an expression
                        _, mt, mm, ms, _ = from_type(func['vars'][p]['typespec'])
                        if 'dimension' not in func['vars'][p]:
                            # not an array
                            cwrap.append(f'    {mt} {magma_params[p]};')
                            if func['vars'][p]['intent'] != ['out']:
                                cwrap.append(f'    {magma_params[p]} = *{p};')
                        else:
                            d = [f'(*{i})' for i in func['vars'][p]['dimension']]
                            #print(t, p, d)
                            #print(func['vars'][p]['intent'])
                            size = ' * '.join(d)
                            cwrap.append(f'    {mt}* {magma_params[p]};')
                            #if func['vars'][p]['intent'] == ['out']:
                            #    cwrap.append(f'    {magma_params[p]} = ({mt}*)malloc({size} * sizeof({mt}));')
                            if t == 'int*':
                                # looks like int variables are always on the host memory
                                cwrap.append(f'    {magma_params[p]} = {p};')
                            else:
                                # has to be allocated in the GPU, be it in or out
                                cwrap.append(f'    err = {mm}(&{magma_params[p]}, {size});')
                                if 'in' in func['vars'][p]['intent']:
                                    # has to be copied to the GPU only if in
                                    prec = {'float*': 's', 'double*': 'd'}[t]
                                    if len(d) == 2:
                                        cwrap.append(f'    magma_{prec}setmatrix({d[0]}, {d[1]}, {p}, {d[0]}, {magma_params[p]}, {d[0]}, queue);')
                                    else:
                                        cwrap.append(f'    magma_{prec}setvector({d[0]}, {p}, 1, {magma_params[p]}, 1, queue);')
            # MAGMA function call
            margs = []
            for p in params:
                p = param_aliases.get(p, p)
                if p in func['vars']:
                    if (func['vars'][p]['intent'] == ['out']) and ('dimension' not in func['vars'][p]):
                        ma = '&'
                    else:
                        ma = ''
                    ma += magma_params[p]
                else:
                    # argument was an expression
                    ma = p
                margs.append(ma)
            margs = ', '.join(margs)
            cwrap.append(f'    magma_{name}_gpu({margs});')
            # copy results from the GPU
            for t, p in zip(types, params):
                if p not in param_aliases:
                    # argument was not a duplicate
                    if p in func['vars']:
                        if 'dimension' in func['vars'][p]:
                            d = [f'(*{i})' for i in func['vars'][p]['dimension']]
                            size = ' * '.join(d)
                            if t != 'int*':
                                _, _, _, _, mg = from_type(func['vars'][p]['typespec'])
                                if 'out' in func['vars'][p]['intent']:
                                    #print(t, p, func['vars'][p]['dimension'])
                                    prec = {'float*': 's', 'double*': 'd'}[t]
                                    if len(d) == 2:
                                        cwrap.append(f'    magma_{prec}getmatrix({d[0]}, {d[1]}, {magma_params[p]}, {d[0]}, {p}, {d[0]}, queue);')
                                    else:
                                        cwrap.append(f'    magma_{prec}getvector({d[0]}, {magma_params[p]}, 1, {p}, 1, queue);')
            for t, p in zip(types, params):
                if p not in param_aliases:
                    # argument was not a duplicate
                    if p in func['vars']:
                        if 'dimension' in func['vars'][p]:
                            if t != 'int*':
                                cwrap.append(f'    magma_free({magma_params[p]});')
            cwrap.append('    magma_queue_destroy(queue);')
            cwrap.append('    magma_finalize;')
            cwrap.append('}')
            cwrap = '\n'.join(cwrap)
            cfile.append(cwrap)
    
    with open(fout, 'wt') as f:
        f.write('\n'.join(cfile))

    with open(fout + '.func', 'wt') as f:
        f.write('ar dv liblapack.a ' + '.o '.join(gpu_func))

if __name__ == '__main__':
    cfname = 'lapack_to_magma.c'
    pyf2magma('flapack.pyf', cfname, ignore_func=['c...', 'z...'], magma_src='../magma/magma-2.4.0/src')
    #pyf2magma('flapack.pyf', cfname, magma_src='../magma/magma-2.4.0/src')
    print(f'Wrote file {cfname}')
