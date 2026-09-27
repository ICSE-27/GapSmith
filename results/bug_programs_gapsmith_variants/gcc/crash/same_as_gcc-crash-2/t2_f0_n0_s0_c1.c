typedef _Float16 TFtype;
_Float16 g;
int n;
void f(TFtype x, TFtype y) {
    g = ((y == x) ? (y + n) : !(x - y));
}
