typedef __bf16 TFtype;
__bf16 g;
int n;
void f(TFtype x, TFtype y) {
    g = (n ? y : !(x - y));
}
