typedef __bf16 TFtype;
void sink(__bf16);
void f(TFtype x, TFtype y, unsigned n) {
    sink((((x - y) > 0) ? (y + n) : !(x - y)));
}
