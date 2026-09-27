void outer() {
    void __attribute__((section(".text"), used)) g() {
        void inner() {}
        inner();
    }
    g();
    void __attribute__((noinline)) h() {}
}
