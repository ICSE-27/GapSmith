void outer() {
    void __attribute__((section(".text"))) g() {}
    void __attribute__((noinline)) h() {}
    g(); h();
}
