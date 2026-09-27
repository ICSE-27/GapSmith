typedef __bf16 TFtype;
int main() {
    TFtype x = (TFtype)3.14;
    TFtype y = (TFtype)1.0;
    _Bool n = 0;
    return (int)((y == x) ? (y + n) : !(x - y));
}
