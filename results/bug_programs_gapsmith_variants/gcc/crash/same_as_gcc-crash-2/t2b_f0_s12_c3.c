typedef _Float16 FT;
void sink(FT);
void f(FT x, FT y, FT m, int n) {
    sink(((x && y) ? m : !(x - y)));
}
