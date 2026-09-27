void outer() {
    void __attribute__((section(".text.hot"))) g() {
        void inner() {}
        inner();
    }
    g();
    void __attribute__((noinline)) h() {}
}
