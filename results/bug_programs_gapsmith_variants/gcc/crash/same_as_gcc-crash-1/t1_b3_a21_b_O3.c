void outer() {
    void __attribute__((noinline)) h() {}
    void __attribute__((section(".text"), used)) g() { h(); }
    g();
}
