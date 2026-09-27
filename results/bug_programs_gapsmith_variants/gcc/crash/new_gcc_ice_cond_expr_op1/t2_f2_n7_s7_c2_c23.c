typedef _Float64 TFtype;
_Float64 f(TFtype x, TFtype y, _Float16 n) {
    _Float64 r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
