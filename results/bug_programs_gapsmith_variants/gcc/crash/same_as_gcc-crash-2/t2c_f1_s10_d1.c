typedef __bf16 FT;
FT f(FT x, FT y, int n) {
    FT t = (y == x) ? (y + n) : !(x - y);
    return t ? t : !(x - y);
}
