void outer() {
    void __attribute__((section(".text"), used)) g() {}
    g();
    void __attribute__((noinline)) h() {}
}
