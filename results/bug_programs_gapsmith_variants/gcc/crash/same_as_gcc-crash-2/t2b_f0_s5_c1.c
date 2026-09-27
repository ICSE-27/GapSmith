typedef _Float16 FT;
FT g;
FT f(FT x, FT y, FT m) {
    int n = 0;
    g = ((x > y) ? (x * y) : !(m + 1));
    return g;
}
