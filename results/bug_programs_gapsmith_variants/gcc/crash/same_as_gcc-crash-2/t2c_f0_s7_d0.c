typedef _Float16 FT;
FT f(FT x, FT y, int n) {
    return n ? ((y == x) ? (y + n) : !(x - y)) : (n ? x : !n);
}
