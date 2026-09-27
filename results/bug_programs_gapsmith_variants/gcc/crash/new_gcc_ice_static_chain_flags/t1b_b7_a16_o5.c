void (*fp)();
void outer() {
    void __attribute__((section(".text"), noinline)) g() {}
    void h() {}
    void k() { fp = g; g(); }
    k();
}
