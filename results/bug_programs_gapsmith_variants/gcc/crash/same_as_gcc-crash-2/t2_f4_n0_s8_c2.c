typedef __bf16 TFtype;
__bf16 f(TFtype x, TFtype y, int n) {
    __bf16 r = (((x - y) > 0) ? (y + n) : !(x - y));
    return r;
}
