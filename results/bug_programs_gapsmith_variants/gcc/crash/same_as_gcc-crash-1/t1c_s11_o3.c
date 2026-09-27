#include <setjmp.h>
jmp_buf jb;
void outer() {
    void __attribute__((section(".text"))) g() { longjmp(jb, 1); }
    if (setjmp(jb) == 0) g();
    void h() {}
}
