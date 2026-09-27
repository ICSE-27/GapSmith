void outer() {
    void __attribute__((section(".text.hot"))) g() {}
    void __attribute__((noinline)) h() {}
    g(); h();
}
