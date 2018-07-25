from numpy.f2py.crackfortran import crackfortran

def pyf2magma(fin, fout, ignore=[]):
    blocks = crackfortran([fin])

    cfile = []
    cfile.append('#include <cuda.h>')
    cfile.append('#include "magma_v2.h"')
    for func in blocks[0]['body'][0]['body']:
        name = func['name']
        if name not in ignore:
            types = func['f2pyenhancements']['callprotoargument'].split(',')
            callstatement = func['f2pyenhancements']['callstatement']
            i0 = callstatement.find('f2py_func') + 11
            i1 = callstatement[i0:].find(')') + i0
            args = callstatement[i0:i1].split(',')
            args = [a+'_'*(args[:i].count(a)) for i, a in enumerate(args)]
            
            cwrap = []
            decl = []
            decl.append(f'void {name}_(')
            proto = []
            for t, a in zip(types, args):
                a = a.lstrip('&')
                proto.append(f'{t} {a}')
            decl.append(', '.join(proto))
            decl.append(') {')
            cwrap.append(''.join(decl))
            cwrap.append('    magma_init();')
            cwrap.append('    magma_queue_t queue = NULL;')
            cwrap.append('    magma_int_t dev = 0;')
            cwrap.append('    magma_queue_create(dev, &queue);')
            cwrap.append('    magma_int_t err;')
            for t, a in zip(types, args):
                if a[-1] != '_':
                    t = t[:-1]
                    if a[0] == '&':
                        is_ref = True
                        a = a[1:]
                    else:
                        is_ref = False
                    if t == 'int':
                        mt = 'magma_int_t'
                        mm = 'magma_imalloc'
                    elif t == 'double':
                        mt = 'double'
                        mm = 'magma_dmalloc'
                    if is_ref:
                        if func['vars'][a]['intent'] == ['out']:
                            cwrap.append(f'    {mt} _{a};')
                        else:
                            cwrap.append(f'    {mt} _{a} = *{a};')
                    elif 'dimension' in func['vars'][a]:
                        d = [f'_{i}' for i in func['vars'][a]['dimension']]
                        size = ' * '.join(d)
                        cwrap.append(f'    {mt}* _{a};')
                        if func['vars'][a]['intent'] == ['out']:
                            cwrap.append(f'    _{a} = ({mt}*)malloc({size} * sizeof({mt}));')
                        else:
                            cwrap.append(f'    err = {mm}(&_{a}, {size});')
                            cwrap.append(f'    magma_dsetmatrix({d[0]}, {d[1]}, {a}, {d[0]}, _{a}, {d[0]}, queue);')
            margs = []
            for a in args:
                a = a.lstrip('&').rstrip('_')
                if (func['vars'][a]['intent'] == ['out']) and ('dimension' not in func['vars'][a]):
                    ma = '&'
                else:
                    ma = ''
                ma += '_' + a
                margs.append(ma)
            margs = ', '.join(margs)
            cwrap.append(f'    magma_{name}_gpu({margs});')
            for t, a in zip(types, args):
                if a[-1] != '_':
                    if a[0] == '&':
                        is_ref = True
                        a = a[1:]
                    else:
                        is_ref = False
                    if (not is_ref) and ('dimension' in func['vars'][a]):
                        d = [f'_{i}' for i in func['vars'][a]['dimension']]
                        size = ' * '.join(d)
                        if func['vars'][a]['intent'] == ['out']:
                            cwrap.append(f'    for (int __i__ = 0; __i__ < {size}; __i__++) {a}[__i__] = _{a}[__i__];');
                        else:
                            cwrap.append(f'    magma_dgetmatrix({d[0]}, {d[1]}, _{a}, {d[0]}, {a}, {d[0]}, queue);')
            for t, a in zip(types, args):
                if a[-1] != '_':
                    if a[0] == '&':
                        is_ref = True
                        a = a[1:]
                    else:
                        is_ref = False
                    if (not is_ref) and ('dimension' in func['vars'][a]):
                        if (func['vars'][a]['intent'] == ['out']):
                            cwrap.append(f'    free(_{a});')
                        else:
                            cwrap.append(f'    magma_free(_{a});')
            cwrap.append('    magma_queue_destroy(queue);')
            cwrap.append('    magma_finalize;')
            cwrap.append('}')
            cwrap = '\n'.join(cwrap)
            cfile.append(cwrap)
    
    with open(fout, 'wt') as f:
        f.write('\n'.join(cfile))

if __name__ == '__main__':
    cfname = 'gesv_to_magma_gesv_gpu.c'
    pyf2magma('flapack.pyf', cfname, ignore=['sgesv', 'cgesv', 'zgesv'])
    print(f'Wrote file {cfname}')
