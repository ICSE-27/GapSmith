int outer(int x) {
    int __attribute__((section("foo"))) g(int v) { return v + 1; }
    int h(int v) { return v * 2; }
    int k(int v) { return g(v) + h(v); }
    return k(x);
}
