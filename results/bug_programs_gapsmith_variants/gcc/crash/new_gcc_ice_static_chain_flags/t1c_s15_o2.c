void outer() {
    void __attribute__((section(".text"))) g() { asm volatile(""); }
    void k() { g(); }
    k();
    void h() {}
}
