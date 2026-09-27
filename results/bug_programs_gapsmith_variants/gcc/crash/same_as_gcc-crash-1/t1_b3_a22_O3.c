void outer() {
    void  h() {}
    void __attribute__((section(".text"), noinline)) g() { h(); }
    g();
}
