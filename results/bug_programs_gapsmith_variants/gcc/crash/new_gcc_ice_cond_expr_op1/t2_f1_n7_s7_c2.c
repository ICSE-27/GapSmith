typedef _Float32 TFtype;
_Float32 f(TFtype x, TFtype y, _Float16 n) {
    _Float32 r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
