typedef __bf16 TFtype;
__bf16 f(TFtype x, TFtype y, long n) {
    __bf16 r = (n ? y : !(x - y));
    return r;
}
