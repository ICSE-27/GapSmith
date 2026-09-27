typedef __bf16 FT;
FT f(FT x, FT m, int n) {
    return n ? ((x < m) ? !(m + 1) : x) : !(x - m);
}