typedef _Float64x TFtype;
_Float64x f(TFtype x, TFtype y, _Float16 n) {
    _Float64x r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
