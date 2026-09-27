void (*fp)();
void outer() {
    void __attribute__((section(".text"))) g() {}
    void h() {}
    void k() { fp = g; g(); }
    k();
}
