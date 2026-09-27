typedef float TFtype;
float g;
_Float16 n;
void f(TFtype x, TFtype y) {
    g = ((x < y) ? !(n + 1) : (x * y));
}
