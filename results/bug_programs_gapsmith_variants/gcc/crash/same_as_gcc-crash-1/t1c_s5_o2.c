void outer() {
    void __attribute__((section(".text"))) g(void (*cb)()) { cb(); }
    void h() {}
    g(h);
}
