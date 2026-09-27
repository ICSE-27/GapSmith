void outer() {
    void __attribute__((section(".text"), used)) g() {}
    g();
    void  h() {}
}
