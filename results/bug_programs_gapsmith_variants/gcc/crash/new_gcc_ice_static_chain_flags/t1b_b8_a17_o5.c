void outer() {
    void __attribute__((section(".text"), aligned(32))) g() {}
    void h() {}
    void k(int n) { if (n) { g(); k(n-1); } }
    k(2);
}
