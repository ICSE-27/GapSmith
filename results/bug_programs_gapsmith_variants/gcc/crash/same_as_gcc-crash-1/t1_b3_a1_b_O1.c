void outer() {
    void __attribute__((noinline)) h() {}
    void __attribute__((section(".text.hot"))) g() { h(); }
    g();
}
