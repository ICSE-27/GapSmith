typedef _Float16 TFtype;
_Float16 f(TFtype x, TFtype y, _Bool n) {
    _Float16 r = (n ? y : !(x - y));
    return r;
}
