typedef __bf16 TFtype;
int main() {
    TFtype x = (TFtype)3.14;
    TFtype y = (TFtype)1.0;
    char n = 0;
    return (int)(((x - y) > 0) ? (y + n) : !(x - y));
}
