typedef __bf16 TFtype;
void sink(__bf16);
void f(TFtype x, TFtype y, long long n) {
    sink(((y == x) ? (y + n) : !(x - y)));
}
