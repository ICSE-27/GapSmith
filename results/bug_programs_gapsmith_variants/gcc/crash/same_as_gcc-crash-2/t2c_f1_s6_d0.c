typedef __bf16 FT;
FT f(FT x, FT y, int n) {
    return ((y == x) ? (y + n) : !(x - y)) + x;
}
