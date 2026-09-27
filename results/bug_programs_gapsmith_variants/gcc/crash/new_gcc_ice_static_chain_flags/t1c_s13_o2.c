#include <stdlib.h>
void outer() {
    void __attribute__((section(".text"), noreturn)) g() { exit(0); }
    void k() { g(); }
    k();
    void h() {}
}
