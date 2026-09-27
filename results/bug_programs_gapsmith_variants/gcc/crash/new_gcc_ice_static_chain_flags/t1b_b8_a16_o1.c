void outer() {
    void __attribute__((section(".text"), noinline)) g() {}
    void h() {}
    void k(int n) { if (n) { g(); k(n-1); } }
    k(2);
}
