"""Campaign t2d: _Float16 excess-precision with NEW axes:
-fexcess-precision flags, C++ mode, _Complex, decimal floats,
__builtin_choose_expr, statement expressions, nested contexts.
"""

def shapes_c():
    for ft in ["_Float16", "__bf16", "_Float32", "_Float128", "_Float64"]:
        # base: float-expr ! in second operand position (5714 vein)
        yield f'''typedef {ft} FT;
FT f(FT x, FT m) {{
    return (x < m) ? !(m + 1) : (x * m);
}}'''
        # complex
        yield f'''typedef _Complex {ft} CT;
{ft} f({ft} x, CT c) {{
    return (x > 0) ? !({ft}__real__ c) : x;
}}'''
        # builtin choose expr
        yield f'''typedef {ft} FT;
FT f(FT x, FT m) {{
    return __builtin_choose_expr(x < m, !(m + 1), x * m);
}}'''
        # statement expression
        yield f'''typedef {ft} FT;
FT f(FT x, FT m) {{
    return ({{ FT t = (x < m) ? !(m + 1) : x; t; }});
}}'''
        # nested ternary with float-! in both branches
        yield f'''typedef {ft} FT;
FT f(FT x, FT m, int n) {{
    return n ? ((x < m) ? !(m + 1) : x) : !(x - m);
}}'''
        # !float feeding comparison
        yield f'''typedef {ft} FT;
int f(FT x, FT m) {{
    return (x < m) ? (!(m + 1) > x) : 0;
}}'''
        # excess precision through call result
        yield f'''typedef {ft} FT;
FT g(FT);
FT f(FT x, FT m) {{
    return (x < m) ? !g(m) : (x * m);
}}'''
        # compare two !floats
        yield f'''typedef {ft} FT;
FT f(FT x, FT m) {{
    return (!(x - m) == !(m - x)) ? x : m;
}}'''

def shapes_dec():
    for dt in ["_Decimal32", "_Decimal64", "_Decimal128"]:
        yield f'''typedef {dt} DT;
DT f(DT x, DT m) {{
    return (x < m) ? !(m + 1) : (x * m);
}}'''
        yield f'''typedef {dt} DT;
DT f(DT x, DT m) {{
    return (x < m) ? (x * m) : !(m + 1);
}}'''

def shapes_cxx():
    for ft in ["_Float16", "__bf16", "float"]:
        yield f'''typedef {ft} FT;
FT f(FT x, FT m) {{
    return (x < m) ? FT(!(m + 1)) : (x * m);
}}'''
        yield f'''template <typename T>
T f(T x, T m) {{
    return (x < m) ? !(m + 1) : (x * m);
}}
template {ft} f<{ft}>({ft}, {ft});'''

CFLAGS = [[], ["-fexcess-precision=standard"], ["-fexcess-precision=fast"],
          ["-std=c23", "-fexcess-precision=standard"], ["-O2"], ["-O2", "-fexcess-precision=standard"]]

def generate():
    i = 0
    for src in shapes_c():
        for fi, fl in enumerate(CFLAGS):
            yield {"name": f"t2d_c{i}_f{fi}", "src": src, "tag": "gcc",
                   "flags": fl, "ext": ".c"}
        i += 1
    for src in shapes_dec():
        for fi, fl in enumerate(CFLAGS[:4]):
            yield {"name": f"t2d_d{i}_f{fi}", "src": src, "tag": "gcc",
                   "flags": fl, "ext": ".c"}
        i += 1
    i = 0
    for src in shapes_cxx():
        for fi, fl in enumerate([[], ["-O2"], ["-std=c++23"]]):
            yield {"name": f"t2d_x{i}_f{fi}", "src": src, "tag": "gxx",
                   "flags": fl, "ext": ".cpp"}
        i += 1
