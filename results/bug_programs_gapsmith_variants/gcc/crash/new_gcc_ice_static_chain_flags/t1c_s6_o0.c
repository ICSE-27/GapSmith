void outer() {
    void __attribute__((section(".text"))) g() { static int s; s++; }
    void k() { g(); }
    k();
    void h() {}
}
