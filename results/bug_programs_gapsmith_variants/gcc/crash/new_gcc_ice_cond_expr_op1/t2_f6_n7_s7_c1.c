typedef _Float64x TFtype;
_Float64x g;
_Float16 n;
void f(TFtype x, TFtype y) {
    g = ((x < y) ? !(n + 1) : (x * y));
}
