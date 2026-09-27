void outer() {
    void  h() {}
    void __attribute__((section(".text"), used)) g() { h(); }
    g();
}
