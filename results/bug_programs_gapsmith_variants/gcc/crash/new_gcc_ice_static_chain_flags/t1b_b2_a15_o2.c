void outer() {
    void __attribute__((section(".text"), used)) g() {}
    void h() { g(); }
    void k() { g(); }
    h(); k();
}
