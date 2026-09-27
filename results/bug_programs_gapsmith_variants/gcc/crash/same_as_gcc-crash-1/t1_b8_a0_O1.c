void outer() {
    static int cnt;
    void __attribute__((section(".text"))) g() { cnt++; }
    g();
    void  h() { cnt--; }
    h();
}
