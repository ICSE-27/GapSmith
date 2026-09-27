typedef __bf16 FT;
FT f(FT x, FT m) {
    return ({ FT t = (x < m) ? !(m + 1) : x; t; });
}