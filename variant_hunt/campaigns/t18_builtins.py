"""Campaign t18: __builtin_* on _BitInt (clz/ctz/popcount/parity/overflow) —
different backend legalization surface than rotate. Run-mode vs 128-bit ref.
Widths <= 64 (lo only, no wide-shift UB), plus a few 65..96 with safe build.
"""

TEMPLATE = '''#include <stdio.h>
#include <stdint.h>
#define W {w}
typedef unsigned _BitInt(W) BT;
__attribute__((noinline))
uint64_t f(uint64_t x) {{
  BT v = (BT)x;
  {body}
}}
__attribute__((noinline))
uint64_t ref(uint64_t x) {{
  volatile uint64_t vx = x;
  __uint128_t v = (__uint128_t)vx & {m};
  {refbody}
}}
int main() {{
  uint64_t s = 0x9e3779b97f4a7c15ULL;
  int bad = 0;
  for (int i = 0; i < 512; i++) {{
    s ^= s << 13; s ^= s >> 7; s ^= s << 17;
    uint64_t inp = s & ((W >= 64) ? ~0ULL : ((1ULL << W) - 1));
    uint64_t r = f(inp), e = ref(inp);
    if (r != e) {{ printf("i=%d got=%llu exp=%llu\\n", i, (unsigned long long)r, (unsigned long long)e); bad++; }}
  }}
  printf(bad ? "RESULT: wrong %d\\n" : "RESULT: correct\\n", bad);
  return bad;
}}
'''

def M(w):
    return f"(((__uint128_t)1 << {w}) - 1)" if w < 128 else "~(__uint128_t)0"

BODIES = [
    # popcount
    ("return (uint64_t)__builtin_popcountg(v);",
     "return (uint64_t)__builtin_popcountll((unsigned long long)(v & {m}));"),
    # clz with width semantics: countl_zero of _BitInt is width-relative
    ("return (uint64_t)__builtin_clzg(v, W);",
     "return v == 0 ? (uint64_t){w} : (uint64_t)(__builtin_clzll((unsigned long long)(v & {m})) - (64 - {w}));"),
    # ctz
    ("return (uint64_t)__builtin_ctzg(v, W);",
     "return v == 0 ? (uint64_t){w} : (uint64_t)__builtin_ctzll((unsigned long long)(v & {m}));"),
    # parity
    ("return (uint64_t)__builtin_parityg(v);",
     "return (uint64_t)__builtin_parityll((unsigned long long)(v & {m}));"),
    # add overflow into wider check
    ("BT r; return __builtin_add_overflow(v, (BT){k}, &r) ? 1000 + (uint64_t)r : (uint64_t)r;",
     "__uint128_t s = (v & {m}) + ({k} & {m}); __uint128_t r = s & {m}; return (s > {m}) ? 1000 + (uint64_t)r : (uint64_t)r;"),
    # sub overflow
    ("BT r; return __builtin_sub_overflow(v, (BT){k}, &r) ? 1000 + (uint64_t)r : (uint64_t)r;",
     "__uint128_t vv = v & {m}; __uint128_t kk = ({k} & {m}); __uint128_t r = (vv - kk) & {m}; return (vv < kk) ? 1000 + (uint64_t)r : (uint64_t)r;"),
    # byteswap-ish via shifts
    ("BT r = ((v << {s}) | (v >> (W - {s}))); return (uint64_t)r;",
     "__uint128_t vv = v & {m}; __uint128_t r = ((vv << {s}) | (vv >> ({w} - {s}))) & {m}; return (uint64_t)r;"),
]

def generate():
    i = 0
    for w in [3, 5, 7, 8, 13, 16, 21, 31, 33, 48, 63, 64]:
        for bi, (body, refbody) in enumerate(BODIES):
            for k in [1, 100, 255]:
                if bi not in (4, 5) and k != 1:
                    continue
                for s in [1, 3]:
                    if bi != 6 and s != 1:
                        continue
                    if bi == 6 and s >= w:
                        continue
                    src = TEMPLATE.format(w=w, m=M(w), body=body.format(k=k, s=s, w=w),
                                          refbody=refbody.format(k=k, s=s, w=w, m=M(w)))
                    yield {"name": f"t18_{i}", "src": src, "tag": "clang",
                           "flags": ["-std=c23"], "mode": "run",
                           "optlevels": ["-O0", "-O1", "-O2"], "ext": ".c"}
                    i += 1
