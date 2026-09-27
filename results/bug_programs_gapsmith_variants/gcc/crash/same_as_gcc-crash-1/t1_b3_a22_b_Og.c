void outer() {
    void __attribute__((noinline)) h() {}
    void __attribute__((section(".text"), noinline)) g() { h(); }
    g();
}
