typedef __bf16 FT;
int main() {
    FT x = (FT)3.14, y = (FT)1.0, m = (FT)0.5;
    int n = 0;
    return (int)((x < y) ? !(m - 1) : (x * y));
}
