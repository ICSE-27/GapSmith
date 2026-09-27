int outer(int x) {
    int __attribute__((section(".text"), aligned(32))) g(int y) { return y + 1; }
    int r = g(x);
    int  h(int y) { return y * 2; }
    return r + h(x);
}
