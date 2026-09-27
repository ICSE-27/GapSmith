typedef _Float128 TFtype;
_Float128 g;
_Float16 n;
void f(TFtype x, TFtype y) {
    g = ((x < y) ? !(n + 1) : (x * y));
}
