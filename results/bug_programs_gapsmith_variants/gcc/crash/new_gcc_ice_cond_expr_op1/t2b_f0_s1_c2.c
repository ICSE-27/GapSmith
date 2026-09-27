typedef _Float16 FT;
FT f(FT x, FT y, FT m, int n) {
    FT r = ((x < y) ? !(m - 1) : (x * y));
    return r;
}
