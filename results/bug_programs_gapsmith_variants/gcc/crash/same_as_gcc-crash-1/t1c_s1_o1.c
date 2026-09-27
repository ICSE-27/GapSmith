struct S { int a, b; };
void outer() {
    struct S __attribute__((section(".text"))) g() { struct S s = {1,2}; return s; }
    struct S r = g();
    void h() {}
}
