typedef _Float16 TFtype;
void sink(_Float16);
void f(TFtype x, TFtype y, double n) {
    sink((((x - y) > 0) ? (y + n) : !(x - y)));
}
