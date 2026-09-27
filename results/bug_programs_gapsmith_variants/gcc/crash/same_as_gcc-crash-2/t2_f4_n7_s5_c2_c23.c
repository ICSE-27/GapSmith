typedef __bf16 TFtype;
__bf16 f(TFtype x, TFtype y, _Float16 n) {
    __bf16 r = (n ? y : !(x - y));
    return r;
}
