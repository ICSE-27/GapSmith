void outer() {
    void  h() {}
    void __attribute__((section(".text"), aligned(32))) g() { h(); }
    g();
}
