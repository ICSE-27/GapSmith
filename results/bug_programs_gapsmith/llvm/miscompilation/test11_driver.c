#include <stdio.h>
long f(long);
int main() {
  int bad = 0;
  for (long a = 0; a < 8192; a++) {
    unsigned long uv = a & 8191;
    unsigned long us = (uv << 2) & 8191;
    unsigned long um = uv & 8188;
    long exp = (us == um) ? 1 : 3;
    long r = f(a << 8);
    printf("a=%ld got=%ld expected=%ld %s\n", a, r, exp, r==exp?"ok":"MISMATCH");
    if (r != exp) bad++;
  }
  return bad;
}
