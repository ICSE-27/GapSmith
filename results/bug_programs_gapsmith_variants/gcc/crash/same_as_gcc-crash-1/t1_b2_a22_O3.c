void outer() {
    void __attribute__((section(".text"), noinline)) g() {}
    void  h() {}
    g(); h();
}
