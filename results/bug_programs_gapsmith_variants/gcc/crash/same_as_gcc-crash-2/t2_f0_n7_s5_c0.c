typedef _Float16 TFtype;
int main() {
    TFtype x = (TFtype)3.14;
    TFtype y = (TFtype)1.0;
    _Float16 n = 0;
    return (int)(n ? y : !(x - y));
}
