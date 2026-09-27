"""Campaign t11b: llc-level IR variants of the _BitInt rotate miscompile.
Generate .ll directly with iN types; check llc output for the rotl fold.
Mode: llc compile + grep for rol in output -> WRONGCODE signature.
We encode as compile-mode with a marker: hunt.py can't grep output, so we
generate a C harness too. Simpler: embed the iN fold in C with _BitInt(N)
across wider widths not covered before, including vector-ish sizes and
shift==width-1 etc. Use run mode with -O0/-O1.
"""

TEMPLATE = '''#include <stdio.h>
#define W {w}
typedef unsigned _BitInt(W) BT;
__attribute__((noinline))
long f(long x) {{
  BT v = (BT)(x >> 8);
  BT s = (BT)(v << {sh});
  BT m = (BT)(v & (BT)({mask}));
  return s == m ? 1 : 3;
}}
__attribute__((noinline))
long ref(long x) {{
  volatile long xl = x;
  unsigned long long uv = ((unsigned long long)(xl >> 8)) & ((1ULL << W) - 1);
  unsigned long long us = (uv << {sh}) & ((1ULL << W) - 1);
  unsigned long long um = (uv & ((unsigned long long)({mask}) & ((1ULL << W) - 1)));
  return (us == um) ? 1 : 3;
}}
int main() {{
  int bad = 0;
  for (long a = 0; a < (1L << W); a++) {{
    long r = f(a << 8), e = ref(a << 8);
    if (r != e) {{ printf("a=%ld got=%ld exp=%ld\\n", a, r, e); bad++; }}
  }}
  printf(bad ? "RESULT: wrong %d\\n" : "RESULT: correct\\n", bad);
  return bad;
}}
'''

def generate():
    i = 0
    for w in list(range(2, 33)) + [36, 40, 48, 56, 64]:
        for sh in range(1, min(w, 7)):
            if w % sh == 0:
                continue  # shift dividing width -> rotate is equivalent
            for mask in ["-4", "-2", "2", "3", "-8"]:
                src = TEMPLATE.format(w=w, sh=sh, mask=mask)
                yield {"name": f"t11b_w{w}_s{sh}_m{mask.replace('-','n')}_{i}",
                       "src": src, "tag": "clang", "flags": ["-std=c23"],
                       "mode": "run", "optlevels": ["-O0", "-O1"],
                       "ext": ".c"}
                i += 1
