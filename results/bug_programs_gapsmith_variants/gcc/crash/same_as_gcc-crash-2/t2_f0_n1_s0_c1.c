typedef _Float16 TFtype;
_Float16 g;
long n;
void f(TFtype x, TFtype y) {
    g = ((y == x) ? (y + n) : !(x - y));
}
