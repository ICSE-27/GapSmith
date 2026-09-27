#include <stdio.h>
#define W 13
typedef unsigned _BitInt(W) BT;
typedef unsigned _BitInt(W+8) WBT;
__attribute__((noinline))
long f(long x) {
  BT v = (BT)(x >> 8);
  BT s = (BT)(v << 2);
  BT m = (BT)(v & (BT)(-4));
  return s != m ? 1 : 3;
}
/* reference: compute in wider type and truncate */
__attribute__((noinline))
long ref(long x) {
  volatile long xl = x;
  unsigned long uv = ((unsigned long)(WBT)(xl >> 8)) & ((1UL << W) - 1);
  unsigned long us = (uv << 2) & ((1UL << W) - 1);
  unsigned long um = (uv & ((unsigned long)(-4) & ((1UL << W) - 1))) & ((1UL << W) - 1);
  return (us != um) ? 1 : 3;
}
int main() {
  int bad = 0;
  for (long a = 0; a < (1 << W); a++) {
    long r = f(a << 8), e = ref(a << 8);
    if (r != e) { printf("a=%ld got=%ld exp=%ld\n", a, r, e); bad++; }
  }
  printf(bad ? "RESULT: wrong %d\n" : "RESULT: correct\n", bad);
  return bad;
}
