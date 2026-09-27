int a = 0, d = 0, f = 0;
long long c[7];
int g(short h) {
  long e = h & 1048575;
  switch (e)
  case 6:
  case 3:
    for (;;)
      ;
  return 0;
}
long i(long long *h, long j) {
  for (int k = 0; k < 7; k++) {
    int b = h[k] ^ j;
    switch ((b + a - 50) % 6u) {
    case 3:
      d += 5;
      break;
    case 0:
      d = b + 7080;
      d = g(b + 050) + b + j + b * 3;
    case 5:
      f = 1;
    case 1:
      d = b + b;
    case 2:
    case 4:
      d ^= 3;
    }
    a = 50;
  }
  return d + j + d + ((char)(d + 7) + d - 3) + f;
}
int main() { i(c, -1); return 0; }
