"""Campaign t2: mutations of gcc/crash/test2.c
Seed: ternary mixing _Float16 with integer logical negation ->
ICE in build_conditional_expr, c/c-typeck.cc:5720 at every -O.
Axes: float type x negation operand type x shape x context x std.
"""

FTYPES = ["_Float16", "_Float32", "_Float64", "_Float128", "__bf16",
          "_Float32x", "_Float64x", "float", "double", "long double"]
NOTYPES = ["int", "long", "short", "char", "unsigned", "float", "double",
           "_Float16", "_Bool", "long long"]

# shape: (cond, branch2-expr template using x,y,n)
SHAPES = [
    "(y == x) ? (y + n) : !(x - y)",          # original
    "(y == x) ? (y + n) : !n",
    "(y != x) ? !n : (y + n)",
    "x ? (y + n) : !n",
    "(x > y) ? y : !n",
    "n ? y : !(x - y)",
    "!n ? x : y",
    "(x < y) ? !(n + 1) : (x * y)",
    "((x - y) > 0) ? (y + n) : !(x - y)",
    "(y == x) ? (y + n) : (!n + x)",
]

CONTEXTS = [
    # return in main
    lambda ft, nt, e: f'''typedef {ft} TFtype;
int main() {{
    TFtype x = (TFtype)3.14;
    TFtype y = (TFtype)1.0;
    {nt} n = 0;
    return (int)({e});
}}''',
    # assignment to global
    lambda ft, nt, e: f'''typedef {ft} TFtype;
{ft} g;
{nt} n;
void f(TFtype x, TFtype y) {{
    g = ({e});
}}''',
    # initializer of local
    lambda ft, nt, e: f'''typedef {ft} TFtype;
{ft} f(TFtype x, TFtype y, {nt} n) {{
    {ft} r = ({e});
    return r;
}}''',
    # call argument
    lambda ft, nt, e: f'''typedef {ft} TFtype;
void sink({ft});
void f(TFtype x, TFtype y, {nt} n) {{
    sink(({e}));
}}''',
    # global initializer (constant expr)
    lambda ft, nt, e: f'''typedef {ft} TFtype;
{ft} x = ({ft})3.14, y = ({ft})1.0;
{ft} g = ({e.replace('(y == x)', '(1)').replace('(y != x)', '(1)').replace('(x > y)', '(1)').replace('(x < y)', '(1)').replace('((x - y) > 0)', '(1)')});
{nt} n;
''',
]

STDS = [[], ["-std=c23"], ["-std=gnu2x"], ["-std=c11"], ["-std=gnu17"]]

def generate():
    for fi, ft in enumerate(FTYPES):
        for ni, nt in enumerate(NOTYPES):
            for si, shape in enumerate(SHAPES):
                for ci, ctx in enumerate(CONTEXTS):
                    src = ctx(ft, nt, shape) + "\n"
                    for std in STDS[:2] if (fi + ni + si + ci) % 3 == 0 else STDS[:1]:
                        tag = f"t2_f{fi}_n{ni}_s{si}_c{ci}{'_' + std[0][5:] if std else ''}"
                        yield {"name": tag, "src": src, "tag": "gcc",
                               "flags": std, "ext": ".c"}
