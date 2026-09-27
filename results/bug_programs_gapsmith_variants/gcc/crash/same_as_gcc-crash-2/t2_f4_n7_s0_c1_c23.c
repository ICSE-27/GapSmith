typedef __bf16 TFtype;
__bf16 g;
_Float16 n;
void f(TFtype x, TFtype y) {
    g = ((y == x) ? (y + n) : !(x - y));
}
