typedef _Float64 TFtype;
void sink(_Float64);
void f(TFtype x, TFtype y, _Float16 n) {
    sink(((x < y) ? !(n + 1) : (x * y)));
}
