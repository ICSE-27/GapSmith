typedef _Float16 TFtype;
_Float16 g;
char n;
void f(TFtype x, TFtype y) {
    g = (((x - y) > 0) ? (y + n) : !(x - y));
}
