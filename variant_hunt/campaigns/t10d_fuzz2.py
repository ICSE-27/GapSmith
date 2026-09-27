"""Campaign t10d: t10 value-fuzz round 2 — same structure as the -O1 segfault
seed, wider random constant sweep (deterministic LCG), run-mode -O0 vs -O1.
"""

BASE = '''int a = {A}, d = {D}, f = {F};
long long c[{N}];
int g(short h) {{
  long e = h & {MASK};
  switch (e)
  case {C1}:
  case {C2}:
    for (;;)
      ;
  return {GRET};
}}
long i(long long *h, long j) {{
  for (int k = 0; k < {N}; k++) {{
    int b = h[k] ^ j;
    switch ((b + a - {SUB}) % {MOD}u) {{
    case {S3}:
      d += {ADD};
      break;
    case {S0}:
      d = b + {K0};
      d = g(b + 0{OCT}) + b + j + b * {MUL};
    case {S5}:
      f = {FV};
    case {S1}:
      d = b + b;
    case {S2}:
    case {S4}:
      d ^= {XV};
    }}
    a = {ASET};
  }}
  return d + j + d + ((char)(d + {CH}) + d - {CM}) + f;
}}
int main() {{ i(c, {JVAL}); return 0; }}
'''

def lcg(seed):
    x = seed & 0x7FFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        yield x

def generate():
    g = lcg(20260927)
    for i in range(3000):
        n = next(g) % 6 + 4            # 4..9
        mod = next(g) % 5 + 3          # 3..7
        cases = list(range(mod + 1))
        c1 = cases[next(g) % len(cases)]
        c2 = cases[next(g) % len(cases)]
        vals = dict(
            A=0, D=0, F=0, N=n, MASK=[1048575, 255, 4095, 65535][next(g) % 4],
            C1=c1, C2=c2, GRET=0, SUB=next(g) % 100, MOD=mod,
            S3=next(g) % (mod + 1), S0=next(g) % (mod + 1), S5=next(g) % (mod + 1),
            S1=next(g) % (mod + 1), S2=next(g) % (mod + 1), S4=next(g) % (mod + 1),
            ADD=next(g) % 16, K0=7080 + next(g) % 100, OCT=50, MUL=next(g) % 5 + 1,
            FV=next(g) % 4, XV=next(g) % 8, ASET=next(g) % 80, CH=next(g) % 16,
            CM=next(g) % 8, JVAL=[-976002, 12345, -1, 0, 777][next(g) % 5],
        )
        src = BASE.format(**vals)
        yield {"name": f"t10d_{i}", "src": src, "tag": "clang",
               "flags": [], "mode": "run", "optlevels": ["-O0", "-O1"],
               "ext": ".c"}
