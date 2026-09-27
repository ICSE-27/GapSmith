void outer() {
    void __attribute__((section(".text"))) g() {}
    g();
    void __attribute__((noinline)) h() {}
    void k() { g(); }
    k();
}
