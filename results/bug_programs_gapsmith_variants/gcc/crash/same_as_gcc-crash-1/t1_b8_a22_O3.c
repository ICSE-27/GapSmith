void outer() {
    static int cnt;
    void __attribute__((section(".text"), noinline)) g() { cnt++; }
    g();
    void  h() { cnt--; }
    h();
}
