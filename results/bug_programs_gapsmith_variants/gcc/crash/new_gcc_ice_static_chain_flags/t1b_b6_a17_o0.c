void outer() {
    static int cnt;
    void __attribute__((section(".text"), aligned(32))) g() { cnt++; }
    void h() {}
    void k() { g(); g(); }
    k();
}
