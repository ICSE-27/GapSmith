void outer() {
    static int cnt;
    void __attribute__((section(".text.hot"))) g() { cnt++; }
    g();
    void  h() { cnt--; }
    h();
}
