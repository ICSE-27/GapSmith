void outer() {
    void __attribute__((noinline)) h() {}
    void __attribute__((section(".text"), aligned(32))) g() { h(); }
    g();
}
