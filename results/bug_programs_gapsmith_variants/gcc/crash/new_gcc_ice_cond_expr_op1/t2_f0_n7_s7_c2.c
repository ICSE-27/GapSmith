typedef _Float16 TFtype;
_Float16 f(TFtype x, TFtype y, _Float16 n) {
    _Float16 r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
