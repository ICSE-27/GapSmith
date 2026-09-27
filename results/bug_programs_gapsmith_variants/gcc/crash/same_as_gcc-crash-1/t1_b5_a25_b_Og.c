void outer() {
    void __attribute__((section(".text"), aligned(32))) g() {
        void inner() {}
        inner();
    }
    g();
    void __attribute__((noinline)) h() {}
}
