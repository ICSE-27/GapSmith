void outer() {
    void __attribute__((section(".text"))) g() {
        void inner() {}
        inner();
    }
    g();
    void  h() {}
}
