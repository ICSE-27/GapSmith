typedef _Float32 TFtype;
_Float32 g;
_Float16 n;
void f(TFtype x, TFtype y) {
    g = ((x < y) ? !(n + 1) : (x * y));
}
