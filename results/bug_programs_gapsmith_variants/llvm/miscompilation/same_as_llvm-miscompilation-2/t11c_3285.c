#include <stdio.h>
#define W 21
typedef unsigned _BitInt(W) BT;
__attribute__((noinline))
long f(long x) {
  BT v = (BT)(x >> 8);
  BT s = (BT)(v << 2); BT m = (BT)(v & (BT)(-4)); return s == m ? 1 : 3;
}
__attribute__((noinline))
long ref(long x) {
  volatile long xl = x;
  unsigned long long v = ((unsigned long long)(xl >> 8)) & ((1ULL << W) - 1);
  unsigned long long s = (v << 2) & ((1ULL<<W)-1); unsigned long long m = v & ((unsigned long long)(-4) & ((1ULL<<W)-1)); return s == m ? 1 : 3;
}
int main() {
  int bad = 0;
  for (long a = 0; a < (1L << W); a++) {
    long r = f(a << 8), e = ref(a << 8);
    if (r != e) { printf("a=%ld got=%ld exp=%ld\n", a, r, e); bad++; }
  }
  printf(bad ? "RESULT: wrong %d\n" : "RESULT: correct\n", bad);
  return bad;
}
