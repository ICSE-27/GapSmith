void outer() {
    void __attribute__((section(".text"), noinline)) g() {}
    g();
    void h() {}
    void k() { g(); }
    k();
}
