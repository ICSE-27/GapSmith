void outer() {
    void __attribute__((section("foo"))) g() {}
    void __attribute__((noinline)) h() {}
    g(); h();
}
