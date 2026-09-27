void outer() {
    void __attribute__((section("foo"))) g() {}
    g();
    void h() {}
    void k() { g(); }
    k();
}
