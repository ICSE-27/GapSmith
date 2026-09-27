typedef float TFtype;
float f(TFtype x, TFtype y, _Float16 n) {
    float r = ((x < y) ? !(n + 1) : (x * y));
    return r;
}
