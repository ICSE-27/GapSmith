typedef __bf16 FT;
FT f(FT x, FT y, FT m, int n) {
    FT r = ((x == y) ? !(m * 2) : !(x - y));
    return r;
}
