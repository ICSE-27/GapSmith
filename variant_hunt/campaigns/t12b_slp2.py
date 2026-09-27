"""Campaign t12b: SLP narrowing vein with -m flags and new ops/types.
The seed: unsigned short compare narrowed to signed 16-bit under SLP at -O2/-O3.
Try: -mavx2/-msse4.2/-mavx512f, other reductions (|, ^, +, min), other int types
(uint8/uint16/uint32 mixes), compare ops, stride combos. Run-mode.
"""

TEMPLATE = '''#include <stdio.h>
unsigned int acc = 0;
{ta} a[{n}][{n}];
{tb} b[{n}];

__attribute__((noinline)) void test() {{
    for (long long i = 0; i < {n}; i += {si})
        for (long long j = 0; j < {n}; j += {sj})
            acc += a[j][i] {red} (a[j][i] {op} b[j]);
}}

/* scalar reference: same loop with volatile barrier to block SLP */
__attribute__((noinline)) unsigned int ref() {{
    unsigned int r = 0;
    for (long long i = 0; i < {n}; i += {si})
        for (long long j = 0; j < {n}; j += {sj}) {{
            volatile {ta} va = a[j][i];
            volatile {tb} vb = b[j];
            r += (unsigned int)(va {red} (va {op} vb));
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

TYPE_PAIRS = [("unsigned short", "short"), ("unsigned short", "unsigned short"),
              ("unsigned char", "signed char"), ("unsigned char", "char"),
              ("unsigned int", "int"), ("short", "unsigned short")]
OPS = [">=", "<=", ">", "<"]
REDS = ["&", "|", "+", "^"]
STRIDES = [(2, 2), (3, 1), (1, 3), (2, 1)]
VALS = [(61035, 14288), (65535, -1), (32768, 32767)]
MFLAGS = [[], ["-mavx2"], ["-msse4.2"], ["-mavx512f"]]

def generate():
    i = 0
    for (ta, tb) in TYPE_PAIRS:
        for op in OPS:
            for red in REDS:
                for (si, sj) in STRIDES:
                    for (av, bv) in VALS:
                        for mi, mf in enumerate(MFLAGS[:2]):
                            n = 6
                            src = TEMPLATE.format(ta=ta, tb=tb, op=op, red=red,
                                                  si=si, sj=sj, n=n, av=av, bv=bv)
                            yield {"name": f"t12b_{i}", "src": src,
                                   "tag": "clangxx", "flags": ["-std=c++11"] + mf,
                                   "mode": "run", "optlevels": ["-O1", "-O2"],
                                   "ext": ".cpp"}
                        i += 1
