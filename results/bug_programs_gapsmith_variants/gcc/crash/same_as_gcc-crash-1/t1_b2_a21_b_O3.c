void outer() {
    void __attribute__((section(".text"), used)) g() {}
    void __attribute__((noinline)) h() {}
    g(); h();
}
