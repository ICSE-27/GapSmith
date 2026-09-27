typedef long double TFtype;
void sink(long double);
void f(TFtype x, TFtype y, _Float16 n) {
    sink(((x < y) ? !(n + 1) : (x * y)));
}
