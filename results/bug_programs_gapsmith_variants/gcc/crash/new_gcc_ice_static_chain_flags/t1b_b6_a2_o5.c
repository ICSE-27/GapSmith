void outer() {
    static int cnt;
    void __attribute__((section("foo"))) g() { cnt++; }
    void h() {}
    void k() { g(); g(); }
    k();
}
