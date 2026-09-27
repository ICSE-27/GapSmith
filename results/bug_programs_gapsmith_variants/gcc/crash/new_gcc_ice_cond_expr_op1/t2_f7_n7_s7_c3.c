typedef float TFtype;
void sink(float);
void f(TFtype x, TFtype y, _Float16 n) {
    sink(((x < y) ? !(n + 1) : (x * y)));
}
