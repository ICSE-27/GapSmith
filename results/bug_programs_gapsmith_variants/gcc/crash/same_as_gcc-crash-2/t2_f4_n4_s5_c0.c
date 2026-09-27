typedef __bf16 TFtype;
int main() {
    TFtype x = (TFtype)3.14;
    TFtype y = (TFtype)1.0;
    unsigned n = 0;
    return (int)(n ? y : !(x - y));
}
