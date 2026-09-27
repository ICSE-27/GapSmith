"""Campaign t11d: WIDE _BitInt (33..120 bits) — legalization area, different
from the rotate fold. Ops: mul/div/mod by constants, add-wrap compare,
xor-not fold, shifts, boundary compares. Reference in unsigned __int128.
Inputs: 512 PRNG values (xorshift), not exhaustive.
"""

TEMPLATE = '''#include <stdio.h>
#include <stdint.h>
#define W {w}
typedef unsigned _BitInt(W) BT;
__attribute__((noinline))
uint64_t f(uint64_t lo, uint64_t hi) {{
  BT v = ((BT)hi << 64) | (BT)lo;
  {body}
}}
/* reference in 128-bit */
__attribute__((noinline))
uint64_t ref(uint64_t lo, uint64_t hi) {{
  volatile uint64_t vlo = lo, vhi = hi;
  __uint128_t v = ((__uint128_t)vhi << 64) | vlo;
  {refbody}
}}
int main() {{
  uint64_t s = 0x123456789abcdef0ULL;
  int bad = 0;
  for (int i = 0; i < 512; i++) {{
    s ^= s << 13; s ^= s >> 7; s ^= s << 17;
    uint64_t lo = s; s ^= s << 13; s ^= s >> 7; s ^= s << 17;
    uint64_t hi = s & ((W >= 64) ? ~0ULL : 0);
    uint64_t r = f(lo, hi), e = ref(lo, hi);
    if (r != e) {{ printf("i=%d got=%llu exp=%llu\\n", i, (unsigned long long)r, (unsigned long long)e); bad++; }}
  }}
  printf(bad ? "RESULT: wrong %d\\n" : "RESULT: correct\\n", bad);
  return bad;
}}
'''

# mask for W bits in 128-bit domain
def M(w):
    return f"(((__uint128_t)1 << {w}) - 1)"

BODIES = [
    # multiply by small constant, compare high part
    ("BT r = v * (BT){k}; return (uint64_t)(r >> (W - 8));",
     "__uint128_t r = (v * {k}ULL) & {m}; return (uint64_t)(r >> ({w} - 8));"),
    # divide by 3/5/7/9
    ("BT r = v / (BT){k}; return (uint64_t)r;",
     "__uint128_t r = v / {k}ULL; return (uint64_t)r;"),
    # modulo
    ("BT r = v % (BT){k}; return (uint64_t)r;",
     "__uint128_t r = v % {k}ULL; return (uint64_t)r;"),
    # add-wrap: (v + k) < v
    ("return ((BT)(v + (BT){k}) < v) ? 1 : 3;",
     "__uint128_t s = (v + {k}ULL) & {m}; return (s < (v & {m})) ? 1 : 3;"),
    # xor-not: (v ^ mask) == ~v
    ("return ((BT)(v ^ (BT)({k})) == (BT)(~v)) ? 1 : 3;",
     "__uint128_t a = (v ^ ({k}ULL)) & {m}; __uint128_t b = (~v) & {m}; return (a == b) ? 1 : 3;"),
    # mul-mul wrap: v*v truncated compare with v<<s
    ("BT r = v * v; BT s2 = (BT)(v << {s}); return (uint64_t)(r ^ s2);",
     "__uint128_t r = (v * v) & {m}; __uint128_t s2 = (v << {s}) & {m}; return (uint64_t)(r ^ s2);"),
    # shift by (W-1), compare against bit test
    ("BT r = (BT)(v >> (W - 1)); return (uint64_t)r + ((v & 1) ? 2 : 0);",
     "__uint128_t r = (v & {m}) >> ({w} - 1); return (uint64_t)r + ((v & 1) ? 2 : 0);"),
    # boundary compares: v < k where k near 2^(W-1)
    ("return (v < (BT)({k})) ? 1 : 3;",
     "return ((v & {m}) < ((__uint128_t)({k}) & {m})) ? 1 : 3;"),
]

def generate():
    i = 0
    for w in [33, 40, 48, 63, 64, 65, 80, 96, 100, 120]:
        for bi, (body, refbody) in enumerate(BODIES):
            for k in [3, 5, 7, 9, 255, 65537]:
                for s in [1, 7]:
                    if bi not in (5, 6) and s != 1:
                        continue
                    kk = k if not (bi == 7) else (1 << (w - 1)) + k
                    src = TEMPLATE.format(
                        w=w,
                        body=body.format(k=kk, s=s, w=w),
                        refbody=refbody.format(k=kk, s=s, w=w, m=M(w)))
                    yield {"name": f"t11d_{i}", "src": src, "tag": "clang",
                           "flags": ["-std=c23"], "mode": "run",
                           "optlevels": ["-O0", "-O1", "-O2"], "ext": ".c"}
                    i += 1
