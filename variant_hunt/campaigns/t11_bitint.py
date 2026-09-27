"""Campaign t11: mutations of llvm/miscompilation/test11.c
Seed: (x << 2) == (x & -4) on _BitInt(3) compiled as rotate -> wrong for 2/8
inputs at -O1/-O2. The bug triggers whenever shift does not divide bit width.
Axes: bit width x shift amount x mask x comparison op x signedness.
Run-mode: self-checking against a reference computed in plain unsigned long.
"""

TEMPLATE = '''#include <stdio.h>
#define W {w}
typedef {sign} _BitInt(W) BT;
typedef {sign} _BitInt(W+8) WBT;
__attribute__((noinline))
long f(long x) {{
  BT v = (BT)(x >> 8);
  BT s = (BT)(v << {sh});
  BT m = (BT)(v & (BT)({mask}));
  return s {op} m ? 1 : 3;
}}
/* reference: compute in wider type and truncate */
__attribute__((noinline))
long ref(long x) {{
  volatile long xl = x;
  unsigned long uv = ((unsigned long)(WBT)(xl >> 8)) & ((1UL << W) - 1);
  unsigned long us = (uv << {sh}) & ((1UL << W) - 1);
  unsigned long um = (uv & ((unsigned long)({mask}) & ((1UL << W) - 1))) & ((1UL << W) - 1);
  return (us {op} um) ? 1 : 3;
}}
int main() {{
  int bad = 0;
  for (long a = 0; a < (1 << W); a++) {{
    long r = f(a << 8), e = ref(a << 8);
    if (r != e) {{ printf("a=%ld got=%ld exp=%ld\\n", a, r, e); bad++; }}
  }}
  printf(bad ? "RESULT: wrong %d\\n" : "RESULT: correct\\n", bad);
  return bad;
}}
'''

OPS = ["==", "!=", "<", "<=", ">", ">="]
MASKS = ["-4", "-2", "-1", "1", "2", "3", "4", "6", "-8"]

def generate():
    i = 0
    for w in range(2, 17):
        for sh in range(1, min(w, 5)):
            for mask in MASKS:
                for op in OPS:
                    for sign in ["unsigned"]:
                        src = TEMPLATE.format(w=w, sh=sh, mask=mask, op=op, sign=sign)
                        yield {"name": f"t11_w{w}_s{sh}_m{mask.replace('-','n')}_o{OPS.index(op)}{'_s' if not sign else ''}",
                               "src": src, "tag": "clang", "flags": ["-std=c23"],
                               "mode": "run",
                               "optlevels": ["-O0", "-O1"],
                               "ext": ".c"}
                        i += 1
