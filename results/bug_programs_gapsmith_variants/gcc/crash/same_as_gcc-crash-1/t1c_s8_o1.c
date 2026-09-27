void outer() {
    void __attribute__((section(".text"))) g() {
        struct L { int x; } l = {1};
        (void)l;
    }
    g();
    void h() {}
}
