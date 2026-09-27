void outer() {
    void __attribute__((section(".text.hot"))) g() {}
    void h() { g(); }
    void k() { g(); }
    h(); k();
}
