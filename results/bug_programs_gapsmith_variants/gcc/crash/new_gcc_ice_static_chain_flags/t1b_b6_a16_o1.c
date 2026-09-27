void outer() {
    static int cnt;
    void __attribute__((section(".text"), noinline)) g() { cnt++; }
    void h() {}
    void k() { g(); g(); }
    k();
}
