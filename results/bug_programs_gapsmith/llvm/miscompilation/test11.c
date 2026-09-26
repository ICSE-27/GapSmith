#include <stdio.h>
__attribute__((noinline))
long f(long x) {
  unsigned _BitInt(3) v = (unsigned _BitInt(3))(x >> 8);
  unsigned _BitInt(3) s = (unsigned _BitInt(3))(v << 2);
  unsigned _BitInt(3) m = (unsigned _BitInt(3))(v & (unsigned _BitInt(3))(-4));
  return s == m ? 1 : 3;
}
int main() {
  int exp[8] = {1,3,1,3,3,1,3,1};
  int bad = 0;
  for (long a = 0; a < 8; a++) {
    long r = f(a << 8);
    if (r != exp[a]) { printf("a=%ld got=%ld expected=%d MISMATCH\n", a, r, exp[a]); bad++; }
  }
  printf(bad ? "RESULT: wrong\n" : "RESULT: correct\n");
  return bad;
}
