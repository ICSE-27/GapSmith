void outer() {
    void __attribute__((section("foo"))) g() {
        void inner() {}
        inner();
    }
    g();
    void __attribute__((noinline)) h() {}
}
