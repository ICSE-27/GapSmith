"""Campaign t10c: structural fuzz around the t10 (-O1 segfault) seed family.
New shapes: nested loops, two switches, goto, recursion, pointer walks,
global arrays of different sizes/types. Run-mode: divergence -O0 vs -O1/-O2/-O3.
"""

import itertools

TEMPLATES = [
    # nested loops + switch
    '''int a{d}, d{d}, f{d};
long long c[{n}];
int g(short h) {{
  long e = h & {mask};
  switch (e)
  case {c1}:
  case {c2}:
    for (;;)
      ;
  return 0;
}}
long i(long long *h, long j) {{
  for (int k = 0; k < {n}; k++)
    for (int m = 0; m < {m2}; m++) {{
      int b = h[k] ^ (j + m);
      switch ((b + a - {sub}) % {mod}u) {{
      case 3: d += {add}; break;
      case 0:
        d = b + {k0};
        d = g(b + 0{oct}) + b + j + b * {mul};
      case 5: f = {fv};
      case 1: d = b + b;
      case 2:
      case 4: d ^= {xv};
      }}
      a = {aset};
    }}
  return d + j + d + ((char)(d + 7) + d - 3) + f;
}}
int main() {{ i(c, {jval}); return 0; }}
''',
    # two sequential switches
    '''int a{d}, d{d}, f{d};
long long c[{n}];
int g(short h) {{
  long e = h & {mask};
  switch (e)
  case {c1}:
  case {c2}:
    for (;;)
      ;
  return 0;
}}
long i(long long *h, long j) {{
  for (int k = 0; k < {n}; k++) {{
    int b = h[k] ^ j;
    switch ((b + a - {sub}) % {mod}u) {{
    case 3: d += {add}; break;
    case 0:
      d = b + {k0};
      d = g(b + 0{oct}) + b + j + b * {mul};
    case 5: f = {fv};
    case 1: d = b + b;
    case 2:
    case 4: d ^= {xv};
    }}
    switch (b & 3u) {{
    case 0: f += 1; break;
    case 1: d += k; break;
    default: break;
    }}
    a = {aset};
  }}
  return d + j + d + ((char)(d + 7) + d - 3) + f;
}}
int main() {{ i(c, {jval}); return 0; }}
''',
    # while loop + goto
    '''int a{d}, d{d}, f{d};
long long c[{n}];
int g(short h) {{
  long e = h & {mask};
  switch (e)
  case {c1}:
  case {c2}:
    for (;;)
      ;
  return 0;
}}
long i(long long *h, long j) {{
  int k = 0;
again:
  if (k >= {n}) goto done;
  {{
    int b = h[k] ^ j;
    switch ((b + a - {sub}) % {mod}u) {{
    case 3: d += {add}; break;
    case 0:
      d = b + {k0};
      d = g(b + 0{oct}) + b + j + b * {mul};
    case 5: f = {fv};
    case 1: d = b + b;
    case 2:
    case 4: d ^= {xv};
    }}
    a = {aset};
  }}
  k++;
  goto again;
done:
  return d + j + d + ((char)(d + 7) + d - 3) + f;
}}
int main() {{ i(c, {jval}); return 0; }}
''',
    # recursion
    '''int a{d}, d{d}, f{d};
long long c[{n}];
int g(short h) {{
  long e = h & {mask};
  switch (e)
  case {c1}:
  case {c2}:
    for (;;)
      ;
  return 0;
}}
long i(long long *h, long j, int depth) {{
  if (depth >= {n}) return d;
  int b = h[depth] ^ j;
  switch ((b + a - {sub}) % {mod}u) {{
  case 3: d += {add}; break;
  case 0:
    d = b + {k0};
    d = g(b + 0{oct}) + b + j + b * {mul};
  case 5: f = {fv};
  case 1: d = b + b;
  case 2:
  case 4: d ^= {xv};
  }}
  a = {aset};
  return i(h, j, depth + 1) + ((char)(d + 7) + d - 3) + f;
}}
int main() {{ i(c, {jval}, 0); return 0; }}
''',
]

def generate():
    i = 0
    for tmpl in TEMPLATES:
        for (n, mask, c1, c2, sub, mod) in itertools.product(
                [5, 7, 9], [1048575, 255, 4095], [0, 2, 4], [1, 3, 6],
                [50, 16], [6, 4]):
            if c1 == c2:
                continue
            for jval in [-976002, 12345]:
                src = tmpl.format(d=0, n=n, mask=mask, c1=c1, c2=c2, m2=2,
                                  sub=sub, mod=mod, add=5, k0=7080, oct=50,
                                  mul=3, fv=1, xv=3, aset=50, jval=jval)
                yield {"name": f"t10c_{i}", "src": src, "tag": "clang",
                       "flags": [], "mode": "run",
                       "optlevels": ["-O0", "-O1", "-O2"], "ext": ".c"}
                i += 1
