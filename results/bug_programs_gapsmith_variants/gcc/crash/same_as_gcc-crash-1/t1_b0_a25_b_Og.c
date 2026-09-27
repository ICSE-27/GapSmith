void outer() {
    void __attribute__((section(".text"), aligned(32))) g() {}
    g();
    void __attribute__((noinline)) h() {}
}
