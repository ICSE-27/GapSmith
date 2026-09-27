typedef __bf16 TFtype;
int main() {
    TFtype x = (TFtype)3.14;
    TFtype y = (TFtype)1.0;
    _Float16 n = 0;
    return (int)((x < y) ? !(n + 1) : (x * y));
}
