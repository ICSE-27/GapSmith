typedef _Float128 TFtype;
_Float128 f(TFtype x, TFtype y, _Float16 n) {
    _Float128 r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
