typedef __bf16 TFtype;
__bf16 g;
long long n;
void f(TFtype x, TFtype y) {
    g = ((y == x) ? (y + n) : !(x - y));
}
