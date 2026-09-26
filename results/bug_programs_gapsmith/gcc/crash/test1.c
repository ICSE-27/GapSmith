void outer() {
    void __attribute__((section(".text"))) g() {}
    g();
    void h() {}
}
