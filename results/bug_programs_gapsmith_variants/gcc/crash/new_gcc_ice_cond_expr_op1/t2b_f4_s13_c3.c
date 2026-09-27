typedef __bf16 FT;
void sink(FT);
void f(FT x, FT y, FT m, int n) {
    sink(((x || y) ? !(m + 1) : y));
}
