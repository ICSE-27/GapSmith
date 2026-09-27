void outer() {
    void  h() {}
    void __attribute__((section(".text"))) g() { h(); }
    g();
}
