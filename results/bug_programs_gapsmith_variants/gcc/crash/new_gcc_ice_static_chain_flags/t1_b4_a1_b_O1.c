void outer() {
    void __attribute__((section(".text.hot"))) g() {}
    g();
    void __attribute__((noinline)) h() {}
    void k() { g(); }
    k();
}
