typedef _Float32 TFtype;
void sink(_Float32);
void f(TFtype x, TFtype y, _Float16 n) {
    sink(((x < y) ? !(n + 1) : (x * y)));
}
