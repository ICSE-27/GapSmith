void outer() {
    void  h() {}
    void __attribute__((section("foo"))) g() { h(); }
    g();
}
