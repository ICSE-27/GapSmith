"""Campaign t2c: wave-3 _Float16/excess-precision in OTHER expression builders.
The seed ICE family is EXCESS_PRECISION_EXPR mishandling in build_conditional_expr.
Probe build_binary_op, comparisons, initializers, returns, calls, _Generic,
switch, compound literals, arrays, casts.
"""

FT = ["_Float16", "__bf16", "_Float32", "_Float128"]

SHAPES = [
    # binary arithmetic mixing _Float16 and int-not
    '''typedef {ft} FT;
FT f(FT x, FT y) {{
    return x + !0;
}}''',
    '''typedef {ft} FT;
FT f(FT x, FT y) {{
    return x * !1;
}}''',
    '''typedef {ft} FT;
FT f(FT x, FT y) {{
    return (x - y) * !0;
}}''',
    # comparison with ! operand
    '''typedef {ft} FT;
int f(FT x, FT y) {{
    return x < !0;
}}''',
    '''typedef {ft} FT;
int f(FT x, FT y) {{
    return !(x - y) < x;
}}''',
    # initializer
    '''typedef {ft} FT;
FT g = (_Float16)1.5 + !0;
int main() {{ return (int)g; }}''',
    # return of ternary nested in binary
    '''typedef {ft} FT;
FT f(FT x, FT y, int n) {{
    return ((y == x) ? (y + n) : !(x - y)) + x;
}}''',
    # nested ternary
    '''typedef {ft} FT;
FT f(FT x, FT y, int n) {{
    return n ? ((y == x) ? (y + n) : !(x - y)) : (n ? x : !n);
}}''',
    # call argument
    '''typedef {ft} FT;
void sink(FT);
void f(FT x, FT y, int n) {{
    sink(x + !n);
}}''',
    # comma expr
    '''typedef {ft} FT;
FT f(FT x, FT y, int n) {{
    return (n, x + !n);
}}''',
    # conditional feeding conditional
    '''typedef {ft} FT;
FT f(FT x, FT y, int n) {{
    FT t = (y == x) ? (y + n) : !(x - y);
    return t ? t : !(x - y);
}}''',
    # switch on ! of float-diff
    '''typedef {ft} FT;
int f(FT x, FT y) {{
    switch (!(x - y)) {{ case 0: return 1; default: return 0; }}
}}''',
    # array subscript with !float
    '''typedef {ft} FT;
int arr[4];
int f(FT x, FT y) {{
    return arr[!(x - y)];
}}''',
    # _Generic selecting on _Float16 expr
    '''typedef {ft} FT;
int f(FT x) {{
    return _Generic((x + !0), FT: 1, default: 0);
}}''',
    # compound literal
    '''typedef {ft} FT;
FT f(FT x) {{
    return *(FT[]){{ x + !0 }};
}}''',
    # statement expression
    '''typedef {ft} FT;
FT f(FT x, int n) {{
    return ({{ FT t = x + !n; t; }});
}}''',
    # cast of !float to float
    '''typedef {ft} FT;
FT f(FT x, FT y) {{
    return (FT)!(x - y);
}}''',
    # shift by !float
    '''typedef {ft} FT;
int f(FT x, FT y) {{
    return 1 << !(x - y);
}}''',
    # logical ops on float diffs
    '''typedef {ft} FT;
int f(FT x, FT y) {{
    return !(x - y) && !(y - x);
}}''',
    # unary minus of !
    '''typedef {ft} FT;
FT f(FT x, FT y) {{
    return -!(x - y);
}}''',
]

STDS = [[], ["-std=c23"]]

def generate():
    for fi, ft in enumerate(FT):
        for si, shape in enumerate(SHAPES):
            src = shape.format(ft=ft) + "\n"
            for stdi, std in enumerate(STDS):
                yield {"name": f"t2c_f{fi}_s{si}_d{stdi}",
                       "src": src, "tag": "gcc", "flags": std, "ext": ".c"}
