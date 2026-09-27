void outer() {
    void  h() {}
    void __attribute__((section(".text.hot"))) g() { h(); }
    g();
}
