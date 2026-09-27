void outer() {
    static int cnt;
    void __attribute__((section(".text"), used)) g() { cnt++; }
    g();
    void __attribute__((noinline)) h() { cnt--; }
    h();
}
