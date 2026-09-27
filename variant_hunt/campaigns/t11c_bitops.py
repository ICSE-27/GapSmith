"""Campaign t11c: _BitInt other-op folds on x86-64 — beyond shift/mask==rotate:
rotate-like (x<<a)|(x>>(w-a)) on non-multiple widths, sub/xor compare chains,
truncation through different widths, multiplication by constants, comparisons
after arithmetic. Reference computed in 64-bit unsigned domain (w<=24).
"""

TEMPLATE = '''#include <stdio.h>
#define W {w}
typedef unsigned _BitInt(W) BT;
__attribute__((noinline))
long f(long x) {{
  BT v = (BT)(x >> 8);
  {body}
}}
__attribute__((noinline))
long ref(long x) {{
  volatile long xl = x;
  unsigned long long v = ((unsigned long long)(xl >> 8)) & ((1ULL << W) - 1);
  {refbody}
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

# (body, refbody) — M(x) masks to W bits
BODIES = [
    # shift pair or -> rotate recognition
    ("BT s = (BT)((v << {a}) | (v >> (W - {a}))); return s == (BT){c} ? 1 : 3;",
     "unsigned long long s = ((v << {a}) | (v >> (W - {a}))) & ((1ULL<<W)-1); return s == ({c}ULL & ((1ULL<<W)-1)) ? 1 : 3;"),
    # shift then mask equality (seed family, other masks)
    ("BT s = (BT)(v << {a}); BT m = (BT)(v & (BT)({m})); return s == m ? 1 : 3;",
     "unsigned long long s = (v << {a}) & ((1ULL<<W)-1); unsigned long long m = v & ((unsigned long long)({m}) & ((1ULL<<W)-1)); return s == m ? 1 : 3;"),
    # sub-then-compare
    ("BT s = (BT)(v - (BT){c}); return s == v ? 1 : 3;",
     "unsigned long long s = (v - {c}ULL) & ((1ULL<<W)-1); return s == v ? 1 : 3;"),
    # xor fold: (v ^ c) == v  <=> c==0 masked
    ("BT s = (BT)(v ^ (BT){c}); return s == v ? 1 : 3;",
     "unsigned long long s = (v ^ ({c}ULL & ((1ULL<<W)-1))); return s == v ? 1 : 3;"),
    # not-compare: (~v) == (W-bit mask ^ v)
    ("BT s = (BT)(~v); BT m = (BT)((BT)({m}) ^ v); return s == m ? 1 : 3;",
     "unsigned long long s = (~v) & ((1ULL<<W)-1); unsigned long long m = (((unsigned long long)({m})) & ((1ULL<<W)-1)) ^ v; return s == m ? 1 : 3;"),
    # multiply by constant then mask compare
    ("BT s = (BT)(v * (BT){c}); BT m = (BT)(v << {a}); return s == m ? 1 : 3;",
     "unsigned long long s = (v * {c}ULL) & ((1ULL<<W)-1); unsigned long long m = (v << {a}) & ((1ULL<<W)-1); return s == m ? 1 : 3;"),
    # compare after add: (v + c) < v  (wrap test)
    ("BT s = (BT)(v + (BT){c}); return s < v ? 1 : 3;",
     "unsigned long long s = (v + {c}ULL) & ((1ULL<<W)-1); return s < v ? 1 : 3;"),
]

def generate():
    i = 0
    for w in [3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 17, 19, 21, 23]:
        for bi, (body, refbody) in enumerate(BODIES):
            for a in [1, 2, 3, 5]:
                if a >= w or (w - a) <= 0:
                    continue
                for c in [1, 2, 4, -4 & 0xFF, 6]:
                    for m in ["-4", "-2", "3", "6"]:
                        if bi >= 2 and m != "-4":
                            continue  # mask axis only for shift-mask bodies
                        src = TEMPLATE.format(w=w, body=body.format(a=a, c=c, m=m),
                                              refbody=refbody.format(a=a, c=c, m=m))
                        yield {"name": f"t11c_{i}", "src": src, "tag": "clang",
                               "flags": ["-std=c23"], "mode": "run",
                               "optlevels": ["-O0", "-O1", "-O2"], "ext": ".c"}
                        i += 1
