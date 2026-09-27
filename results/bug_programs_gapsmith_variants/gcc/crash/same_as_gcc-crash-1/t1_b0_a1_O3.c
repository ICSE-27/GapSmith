void outer() {
    void __attribute__((section(".text.hot"))) g() {}
    g();
    void  h() {}
}
