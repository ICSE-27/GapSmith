typedef _Float16 FT;
FT f(FT x, FT m) {
    return (x < m) ? !(m + 1) : (x * m);
}