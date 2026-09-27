typedef _Float16 TFtype;
_Float16 g;
double n;
void f(TFtype x, TFtype y) {
    g = ((y == x) ? (y + n) : !(x - y));
}
