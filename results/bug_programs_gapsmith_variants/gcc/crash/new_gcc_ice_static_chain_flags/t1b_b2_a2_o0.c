void outer() {
    void __attribute__((section("foo"))) g() {}
    void h() { g(); }
    void k() { g(); }
    h(); k();
}
