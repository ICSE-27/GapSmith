typedef long double TFtype;
long double f(TFtype x, TFtype y, _Float16 n) {
    long double r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
