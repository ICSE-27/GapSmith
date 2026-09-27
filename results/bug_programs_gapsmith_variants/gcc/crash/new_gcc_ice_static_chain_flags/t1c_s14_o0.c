#include <stdarg.h>
void outer() {
    void __attribute__((section(".text"))) g(const char *f, ...) {
        va_list ap; va_start(ap, f); va_end(ap);
    }
    void h() { g("x"); }
    void k() { g("y", 1); }
    h(); k();
}
