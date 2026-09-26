#include <stdio.h>
long f(long);
int main() {
  int exp[8] = {1,3,1,3,3,1,3,1};
  int bad = 0;
  for (long a = 0; a < 8; a++) {
    long r = f(a << 8);
    printf("a=%ld got=%ld expected=%d %s\n", a, r, exp[a], r==exp[a]?"ok":"MISMATCH");
    if (r != exp[a]) bad++;
  }
  return bad;
}
