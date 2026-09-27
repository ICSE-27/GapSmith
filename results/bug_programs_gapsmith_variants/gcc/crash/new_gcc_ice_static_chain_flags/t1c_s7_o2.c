void outer() {
    void __attribute__((section(".text"))) g() {}
    void __attribute__((used)) h() { g(); }
    void k() { h(); g(); }
    k();
}
