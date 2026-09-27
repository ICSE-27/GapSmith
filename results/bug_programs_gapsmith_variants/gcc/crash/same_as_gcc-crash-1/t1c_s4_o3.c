#include <alloca.h>
void outer() {
    void __attribute__((section(".text"))) g() { void *p = alloca(16); (void)p; }
    g();
    void h() {}
}
