void outer() {
    static int cnt;
    void __attribute__((section(".text.hot"))) g() { cnt++; }
    void h() {}
    void k() { g(); g(); }
    k();
}
