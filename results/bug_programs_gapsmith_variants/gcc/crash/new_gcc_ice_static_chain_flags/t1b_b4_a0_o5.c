void outer() {
    void __attribute__((section(".text"))) g() {}
    void h() { g(); }
    void k() { g(); h(); }
    k();
}
