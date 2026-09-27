void (*fp)();
void outer() {
    void __attribute__((section("foo"))) g() {}
    void h() {}
    void k() { fp = g; g(); }
    k();
}
