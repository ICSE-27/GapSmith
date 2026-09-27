typedef _Float16 TFtype;
void sink(_Float16);
void f(TFtype x, TFtype y, int n) {
    sink(((y == x) ? (y + n) : !(x - y)));
}
