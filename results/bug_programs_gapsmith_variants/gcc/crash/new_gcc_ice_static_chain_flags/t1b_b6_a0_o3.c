void outer() {
    static int cnt;
    void __attribute__((section(".text"))) g() { cnt++; }
    void h() {}
    void k() { g(); g(); }
    k();
}
