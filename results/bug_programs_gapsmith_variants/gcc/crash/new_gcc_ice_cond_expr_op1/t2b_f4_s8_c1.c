typedef __bf16 FT;
FT g;
FT f(FT x, FT y, FT m) {
    int n = 0;
    g = ((x == y) ? !(m * 2) : !(x - y));
    return g;
}
