void outer(int n) {
    void __attribute__((section(".text"))) g() { int vla[n]; vla[0] = 1; }
    g();
    void h() {}
}
