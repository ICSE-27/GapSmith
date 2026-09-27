void outer() {
    void __attribute__((section(".text"), aligned(32))) g() {}
    void  h() {}
    g(); h();
}
