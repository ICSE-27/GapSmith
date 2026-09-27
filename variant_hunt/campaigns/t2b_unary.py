"""Campaign t2b: wave-2 around the NEW c-typeck.cc:5714 ICE
(found when the ! operand is itself a float expression: !(n + 1)).
Expand: float-typed ! operand x branch position x comparison x types.
Also probe other unary ops (~, -, +, ++/--) in ternary branches.
"""

FTYPES = ["_Float16", "_Float32", "_Float64", "_Float128", "__bf16", "float", "double"]

# each shape has two branch exprs using x, y (floats) and m (float), n (int)
SHAPES = [
    "(x < y) ? !(m + 1) : (x * y)",     # wave-1 winner (5714)
    "(x < y) ? !(m - 1) : (x * y)",
    "(x < y) ? !m : (x * y)",
    "(x < y) ? !(x - y) : m",
    "(x < y) ? !(x + y) : m",
    "(x > y) ? (x * y) : !(m + 1)",
    "(x > y) ? (x * y) : !m",
    "(x > y) ? (x * y) : !(x - y)",
    "(x == y) ? !(m * 2) : !(x - y)",
    "(x != y) ? -m : (x * y)",
    "(x != y) ? ~n : (x * y)",
    "(x != y) ? (x * y) : -m",
    "(x && y) ? m : !(x - y)",
    "(x || y) ? !(m + 1) : y",
    "!(m + 1) ? x : y",
    "!m ? (x * y) : (x + y)",
]

CONTEXTS = [
    lambda ft, e: f'''typedef {ft} FT;
int main() {{
    FT x = (FT)3.14, y = (FT)1.0, m = (FT)0.5;
    int n = 0;
    return (int)({e});
}}''',
    lambda ft, e: f'''typedef {ft} FT;
FT g;
FT f(FT x, FT y, FT m) {{
    int n = 0;
    g = ({e});
    return g;
}}''',
    lambda ft, e: f'''typedef {ft} FT;
FT f(FT x, FT y, FT m, int n) {{
    FT r = ({e});
    return r;
}}''',
    lambda ft, e: f'''typedef {ft} FT;
void sink(FT);
void f(FT x, FT y, FT m, int n) {{
    sink(({e}));
}}''',
]

def generate():
    for fi, ft in enumerate(FTYPES):
        for si, shape in enumerate(SHAPES):
            for ci, ctx in enumerate(CONTEXTS):
                src = ctx(ft, shape) + "\n"
                yield {"name": f"t2b_f{fi}_s{si}_c{ci}",
                       "src": src, "tag": "gcc", "flags": [], "ext": ".c"}
