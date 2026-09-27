int outer(int x) {
    int __attribute__((section(".text"))) g(int y) { return y + 1; }
    int r = g(x);
    int __attribute__((noinline)) h(int y) { return y * 2; }
    return r + h(x);
}
