void outer() {
    register int r = 5;
    void __attribute__((section(".text"))) g() { r++; }
    void k() { g(); }
    k();
    void h() {}
}
