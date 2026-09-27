typedef double TFtype;
double f(TFtype x, TFtype y, _Float16 n) {
    double r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
