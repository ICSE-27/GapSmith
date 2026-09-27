typedef _Float16 TFtype;
_Float16 g;
float n;
void f(TFtype x, TFtype y) {
    g = (n ? y : !(x - y));
}
