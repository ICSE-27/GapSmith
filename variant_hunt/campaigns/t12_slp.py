"""Campaign t12: mutations of llvm/miscompilation/test12.cpp
Seed: -O2/-O3 SLP-vectorizes unsigned-short comparison as signed 16-bit cmp;
acc=1 instead of 9. -O0/-O1 correct.
Run-mode. Axes: element types x dims x stride x comparison x value pairs.
"""

TEMPLATE = '''#include <stdio.h>
unsigned int acc = 0;
{ta} a[{n}][{n}];
{tb} b[{n}];

__attribute__((noinline)) void test() {{
    for (long long i = 0; i < {n}; i += {si})
        for (long long j = 0; j < {n}; j += {sj})
            acc += a[j][i] & (a[j][i] {op} b[j]);
}}

int main() {{
    for (int i = 0; i < {n}; i++) {{
        b[i] = {bv};
        for (int j = 0; j < {n}; j++) a[i][j] = {av};
    }}
    test();
    printf("acc=%u (expected {exp})\\n", acc);
    return acc != {exp};
}}
'''

import itertools

def gen_cases():
    # (ta, tb, op, av, bv, expected-count computed below)
    types = [("unsigned short", "short"), ("unsigned short", "unsigned short"),
             ("short", "unsigned short"), ("unsigned char", "char"),
             ("unsigned char", "signed char"), ("unsigned int", "int"),
             ("char", "unsigned char")]
    ops = [">=", "<=", ">", "<", "==", "!="]
    for (ta, tb) in types:
        for op in ops:
            for si, sj in [(2, 2), (1, 2), (2, 1), (3, 1)]:
                for n in [6, 8]:
                    yield (ta, tb, op, si, sj, n)

def expected(ta, tb, op, av, bv, n, si, sj):
    # emulate comparison with C semantics: usual arithmetic conversions
    def conv(t, v):
        if t == "unsigned short": return v & 0xFFFF
        if t == "short": return ((v + 2**15) % 2**16) - 2**15
        if t == "unsigned char": return v & 0xFF
        if t in ("char", "signed char"): return ((v + 2**7) % 2**8) - 2**7
        if t == "unsigned int": return v & 0xFFFFFFFF
        if t == "int": return ((v + 2**31) % 2**32) - 2**31
        return v
    a = conv(ta, av); b = conv(tb, bv)
    # integer promotion: both to int (or unsigned int for unsigned int)
    if ta == "unsigned int" or tb == "unsigned int" or tb == "int":
        ua, ub = conv("unsigned int", a), conv("unsigned int", b)
    else:
        ua, ub = a, b  # promoted to int, signed compare
    cmpfn = {">=": lambda x, y: x >= y, "<=": lambda x, y: x <= y,
             ">": lambda x, y: x > y, "<": lambda x, y: x < y,
             "==": lambda x, y: x == y, "!=": lambda x, y: x != y}[op]
    c = 1 if cmpfn(ua, ub) else 0
    cnt = len(range(0, n, si)) * len(range(0, n, sj))
    return conv(ta, av) & c * cnt  # acc += a & cmp  (cmp is 0/1 -> a & 1)

def generate():
    i = 0
    for (ta, tb, op, si, sj, n) in gen_cases():
        for av, bv in [(61035, 14288), (40000, 40000), (65535, -1), (32768, 32767), (100, 100), (255, 127)]:
            exp = expected(ta, tb, op, av, bv, n, si, sj)
            src = TEMPLATE.format(ta=ta, tb=tb, op=op, si=si, sj=sj, n=n,
                                  av=av, bv=bv, exp=exp)
            yield {"name": f"t12_{i}", "src": src, "tag": "clangxx",
                   "flags": ["-std=c++11"], "mode": "run",
                   "optlevels": ["-O1", "-O2"],
                   "ext": ".cpp"}
            i += 1
