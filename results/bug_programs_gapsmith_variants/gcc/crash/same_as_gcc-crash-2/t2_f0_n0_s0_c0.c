typedef _Float16 TFtype;
int main() {
    TFtype x = (TFtype)3.14;
    TFtype y = (TFtype)1.0;
    int n = 0;
    return (int)((y == x) ? (y + n) : !(x - y));
}
