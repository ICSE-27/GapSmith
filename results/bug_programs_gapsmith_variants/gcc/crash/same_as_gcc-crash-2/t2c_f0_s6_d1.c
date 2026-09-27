typedef _Float16 FT;
FT f(FT x, FT y, int n) {
    return ((y == x) ? (y + n) : !(x - y)) + x;
}
