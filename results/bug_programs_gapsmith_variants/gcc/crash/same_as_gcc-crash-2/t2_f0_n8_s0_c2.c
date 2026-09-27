typedef _Float16 TFtype;
_Float16 f(TFtype x, TFtype y, _Bool n) {
    _Float16 r = ((y == x) ? (y + n) : !(x - y));
    return r;
}
