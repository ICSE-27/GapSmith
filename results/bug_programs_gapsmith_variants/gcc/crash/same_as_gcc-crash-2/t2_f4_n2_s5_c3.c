typedef __bf16 TFtype;
void sink(__bf16);
void f(TFtype x, TFtype y, short n) {
    sink((n ? y : !(x - y)));
}
