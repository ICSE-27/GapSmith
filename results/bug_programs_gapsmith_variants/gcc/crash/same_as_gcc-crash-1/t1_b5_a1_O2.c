void outer() {
    void __attribute__((section(".text.hot"))) g() {
        void inner() {}
        inner();
    }
    g();
    void  h() {}
}
