void outer() {
    void __attribute__((section(".text"), noinline)) g() {}
    void __attribute__((noinline)) h() {}
    g(); h();
}
