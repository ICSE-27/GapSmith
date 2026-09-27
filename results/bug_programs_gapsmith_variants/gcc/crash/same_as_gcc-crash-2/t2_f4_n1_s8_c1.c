typedef __bf16 TFtype;
__bf16 g;
long n;
void f(TFtype x, TFtype y) {
    g = (((x - y) > 0) ? (y + n) : !(x - y));
}
