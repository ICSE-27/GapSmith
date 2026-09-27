typedef _Float16 TFtype;
void sink(_Float16);
void f(TFtype x, TFtype y, unsigned n) {
    sink((n ? y : !(x - y)));
}
