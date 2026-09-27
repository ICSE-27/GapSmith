typedef _Float16 TFtype;
_Float16 f(TFtype x, TFtype y, long long n) {
    _Float16 r = (n ? y : !(x - y));
    return r;
}
