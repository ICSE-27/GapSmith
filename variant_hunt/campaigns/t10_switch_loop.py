"""Campaign t10: mutations of llvm/miscompilation/test10.c
Seed: Clang -O1 miscompiles switch/loop -> binary segfaults; other -O fine.
Run-mode across opt levels. Mutate constants, cases, loop bounds, array size.
"""

TEMPLATE = '''int a = {d_a}, d = {d_d}, f = {d_f};
long long c[{n}];
int g(short h) {{
  long e = h & {mask};
  switch (e)
  case {c1}:
  case {c2}:
    for (;;)
      ;
  return {gret};
}}
long i(long long *h, long j) {{
  for (int k = 0; k < {n}; k++) {{
    int b = h[k] ^ j;
    switch ((b + a - {sub}) % {mod}u) {{
    case 3:
      d += {add};
      break;
    case 0:
      d = b + {k0};
      d = g(b + 0{oct}) + b + j + b * {mul};
    case 5:
      f = {fval};
    case 1:
      d = b + b;
    case 2:
    case 4:
      d ^= {xorv};
    }}
    a = {aset};
  }}
  return d + j + d + ((char)(d + {ch}) + d - 3) + f;
}}
int main() {{ i(c, {jval}); return 0; }}
'''

import itertools

def generate():
    i = 0
    for (n, mask, c1, c2, sub, mod) in itertools.product(
            [5, 7, 4],          # n
            [1048575, 255, 15, 4095],
            [4, 0, 2, 6],
            [6, 1, 3],
            [50, 0, 16, 100],
            [6, 4, 8, 3]):
        if c1 == c2:
            continue
        for jval in [-976002, 0, 12345, -1]:
            src = TEMPLATE.format(
                d_a=0, d_d=0, d_f=0, n=n, mask=mask, c1=c1, c2=c2,
                gret=0, sub=sub, mod=mod, add=5, k0=7080, oct=50,
                mul=3, fval=1, xorv=3, aset=50, ch=7, jval=jval)
            yield {"name": f"t10_{i}", "src": src, "tag": "clang",
                   "flags": [], "mode": "run",
                   "optlevels": ["-O0", "-O1"],
                   "ext": ".c"}
            i += 1
