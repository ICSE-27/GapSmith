typedef _Float32x TFtype;
_Float32x f(TFtype x, TFtype y, _Float16 n) {
    _Float32x r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
