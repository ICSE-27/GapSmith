"""Campaign t12c: SLP/vectorizer NEW axes: float compares, min/max idioms,
reduction of products, bool/char accumulation, -mavx2/-mavx512f, -O3/-Os.
Runtime scalar reference via volatile barrier (like t12b).
"""

TEMPLATE = '''#include <stdio.h>
unsigned int acc = 0;
{ta} a[{n}][{n}];
{tb} b[{n}];

__attribute__((noinline)) void test() {{
    for (long long i = 0; i < {n}; i += {si})
        for (long long j = 0; j < {n}; j += {sj})
            {stmt}
}}

__attribute__((noinline)) unsigned int ref() {{
    unsigned int r = 0;
    for (long long i = 0; i < {n}; i += {si})
        for (long long j = 0; j < {n}; j += {sj}) {{
            volatile {ta} va = a[j][i];
            volatile {tb} vb = b[j];
            {refstmt}
        }}
    return r;
}}

int main() {{
    for (int i = 0; i < {n}; i++) {{
        b[i] = {bv};
        for (int j = 0; j < {n}; j++) a[i][j] = {av};
    }}
    test();
    unsigned int e = ref();
    printf("acc=%u ref=%u\\n", acc, e);
    return acc != e;
}}
'''

# (stmt, refstmt) — {acc} handled inline; note volatile vars va/vb in ref
BODIES = [
    ("acc += a[j][i] & (a[j][i] >= b[j]);",
     "r += (unsigned int)(va & (va >= vb));"),
    # float compare accumulated
    ("acc += (a[j][i] >= b[j]);",
     "r += (unsigned int)(va >= vb);"),
    # min idiom
    ("acc += a[j][i] < b[j] ? a[j][i] : b[j];",
     "r += (unsigned int)(va < vb ? va : vb);"),
    # max idiom
    ("acc += a[j][i] > b[j] ? a[j][i] : b[j];",
     "r += (unsigned int)(va > vb ? va : vb);"),
    # product reduction
    ("acc += a[j][i] * (a[j][i] >= b[j]);",
     "r += (unsigned int)(va * (va >= vb));"),
    # bool accumulation of xor
    ("acc += (a[j][i] ^ b[j]) != 0;",
     "r += (unsigned int)((va ^ vb) != 0);"),
    # select-add
    ("acc += (a[j][i] <= b[j]) ? a[j][i] : 0;",
     "r += (unsigned int)((va <= vb) ? va : 0);"),
]

TYPE_PAIRS = [("unsigned short", "short"), ("unsigned short", "unsigned short"),
              ("unsigned char", "signed char"), ("short", "short"),
              ("float", "float"), ("unsigned int", "int")]
VALS = [("61035", "14288"), ("65535", "-1"), ("32768", "32767"),
        ("200", "100"), ("1.5f", "1.5f"), ("-2.5f", "-3.5f")]
STRIDES = [(2, 2), (3, 1), (1, 3)]
MFLAGS = [[], ["-mavx2"]]
OPTS = ["-O2", "-O3", "-Os"]

def generate():
    i = 0
    for (ta, tb) in TYPE_PAIRS:
        isfloat = "float" in ta
        for bi, (stmt, refstmt) in enumerate(BODIES):
            if isfloat and bi in (0, 4, 5):
                continue  # bitwise ops invalid on floats
            for (si, sj) in STRIDES:
                for (av, bv) in VALS:
                    if isfloat and not av.endswith("f"):
                        continue
                    if not isfloat and av.endswith("f"):
                        continue
                    for mi, mf in enumerate(MFLAGS):
                        src = TEMPLATE.format(ta=ta, tb=tb, n=6, si=si, sj=sj,
                                              stmt=stmt, refstmt=refstmt, av=av, bv=bv)
                        yield {"name": f"t12c_{i}", "src": src, "tag": "clangxx",
                               "flags": ["-std=c++11"] + mf,
                               "mode": "run",
                               "optlevels": ["-O1"] + OPTS[:1] if i % 2 else ["-O1", "-O3"],
                               "ext": ".cpp"}
                    i += 1
