typedef __bf16 FT;
FT f(FT x, FT y, FT m, int n) {
    FT r = ((x < y) ? !(x + y) : m);
    return r;
}
