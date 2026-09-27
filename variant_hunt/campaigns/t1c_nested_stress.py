"""Campaign t1c: wave-3 GCC nested-function stress.
Seed family: nested fns + attributes crash GCC (tree-nested.cc segfault,
gimple_call_static_chain_flags assert). Hunt for MORE distinct signatures:
varargs, struct returns, VLAs, computed goto, alloca, setjmp, register vars,
attribute on variables, mixed with goto labels as values.
"""

SHAPES = [
    # section attr + varargs nested fn
    '''#include <stdarg.h>
void outer() {
    void __attribute__((section(".text"))) g(int n, ...) {
        va_list ap; va_start(ap, n); va_end(ap);
    }
    g(1, 2);
    void h() {}
}''',
    # section attr + struct return
    '''struct S { int a, b; };
void outer() {
    struct S __attribute__((section(".text"))) g() { struct S s = {1,2}; return s; }
    struct S r = g();
    void h() {}
}''',
    # section attr + VLA
    '''void outer(int n) {
    void __attribute__((section(".text"))) g() { int vla[n]; vla[0] = 1; }
    g();
    void h() {}
}''',
    # section attr + computed goto
    '''void outer() {
    void __attribute__((section(".text"))) g(int i) {
        static void *tab[] = { &&l0, &&l1 };
        goto *tab[i & 1];
      l0: return;
      l1: return;
    }
    g(0);
    void h() {}
}''',
    # section attr + alloca
    '''#include <alloca.h>
void outer() {
    void __attribute__((section(".text"))) g() { void *p = alloca(16); (void)p; }
    g();
    void h() {}
}''',
    # attr on nested fn taking ptr to nested fn
    '''void outer() {
    void __attribute__((section(".text"))) g(void (*cb)()) { cb(); }
    void h() {}
    g(h);
}''',
    # nested fn with static var + attr + caller
    '''void outer() {
    void __attribute__((section(".text"))) g() { static int s; s++; }
    void k() { g(); }
    k();
    void h() {}
}''',
    # attr on h too, k calls both
    '''void outer() {
    void __attribute__((section(".text"))) g() {}
    void __attribute__((used)) h() { g(); }
    void k() { h(); g(); }
    k();
}''',
    # nested fn with nested struct + attr
    '''void outer() {
    void __attribute__((section(".text"))) g() {
        struct L { int x; } l = {1};
        (void)l;
    }
    g();
    void h() {}
}''',
    # two section attrs on different nested fns + cross call
    '''void outer() {
    void __attribute__((section(".text.a"))) g() {}
    void __attribute__((section(".text.b"))) h() { g(); }
    h();
}''',
    # label address taken across nested fns
    '''void outer() {
    void *p;
    void __attribute__((section(".text"))) g() { p = &&done; }
    void k() { g(); goto *p; }
    k();
  done: ;
}''',
    # longjmp-style: setjmp in outer, longjmp in nested
    '''#include <setjmp.h>
jmp_buf jb;
void outer() {
    void __attribute__((section(".text"))) g() { longjmp(jb, 1); }
    if (setjmp(jb) == 0) g();
    void h() {}
}''',
    # register var captured
    '''void outer() {
    register int r = 5;
    void __attribute__((section(".text"))) g() { r++; }
    void k() { g(); }
    k();
    void h() {}
}''',
    # attr + noreturn nested fn
    '''#include <stdlib.h>
void outer() {
    void __attribute__((section(".text"), noreturn)) g() { exit(0); }
    void k() { g(); }
    k();
    void h() {}
}''',
    # variadic + attr + called by two
    '''#include <stdarg.h>
void outer() {
    void __attribute__((section(".text"))) g(const char *f, ...) {
        va_list ap; va_start(ap, f); va_end(ap);
    }
    void h() { g("x"); }
    void k() { g("y", 1); }
    h(); k();
}''',
    # inline asm in nested attr fn
    '''void outer() {
    void __attribute__((section(".text"))) g() { asm volatile(""); }
    void k() { g(); }
    k();
    void h() {}
}''',
]

OPTS = [["-O1"], ["-O2"], ["-Os"], ["-Og"], ["-O0"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for oi, o in enumerate(OPTS):
            yield {"name": f"t1c_s{si}_o{oi}", "src": src, "tag": "gcc",
                   "flags": o, "ext": ".c"}
