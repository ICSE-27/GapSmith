void outer() {
    static int cnt;
    void __attribute__((section("foo"))) g() { cnt++; }
    g();
    void  h() { cnt--; }
    h();
}
