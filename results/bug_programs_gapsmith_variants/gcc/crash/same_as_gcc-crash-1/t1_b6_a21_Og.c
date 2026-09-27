int outer(int x) {
    int __attribute__((section(".text"), used)) g(int y) { return y + 1; }
    int r = g(x);
    int  h(int y) { return y * 2; }
    return r + h(x);
}
