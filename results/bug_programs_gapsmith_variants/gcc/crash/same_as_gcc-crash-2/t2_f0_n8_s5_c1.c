typedef _Float16 TFtype;
_Float16 g;
_Bool n;
void f(TFtype x, TFtype y) {
    g = (n ? y : !(x - y));
}
