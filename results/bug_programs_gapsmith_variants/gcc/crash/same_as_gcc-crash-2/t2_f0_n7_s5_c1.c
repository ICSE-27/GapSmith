typedef _Float16 TFtype;
_Float16 g;
_Float16 n;
void f(TFtype x, TFtype y) {
    g = (n ? y : !(x - y));
}
