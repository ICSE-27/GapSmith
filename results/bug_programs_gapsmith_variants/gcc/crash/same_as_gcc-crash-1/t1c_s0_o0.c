#include <stdarg.h>
void outer() {
    void __attribute__((section(".text"))) g(int n, ...) {
        va_list ap; va_start(ap, n); va_end(ap);
    }
    g(1, 2);
    void h() {}
}
