void outer() {
    void __attribute__((section(".text"))) g(int i) {
        static void *tab[] = { &&l0, &&l1 };
        goto *tab[i & 1];
      l0: return;
      l1: return;
    }
    g(0);
    void h() {}
}
