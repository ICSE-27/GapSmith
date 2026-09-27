typedef _Float64x TFtype;
void sink(_Float64x);
void f(TFtype x, TFtype y, _Float16 n) {
    sink(((x < y) ? !(n + 1) : (x * y)));
}
