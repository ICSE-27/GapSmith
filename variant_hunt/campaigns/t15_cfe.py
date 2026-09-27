"""Campaign t15: C front-end combos with _Generic, statement expressions,
_BitInt in switches, VLA, compound literals — hunting NEW C-FE crash sites
in Clang (different from the C++ template veins).
Compile-mode (crash/error).
"""

SHAPES = [
    # _Generic on _BitInt expression
    '''int f(unsigned _BitInt(7) x) {
    return _Generic((x + 1), unsigned _BitInt(7): 1, unsigned _BitInt(8): 2, default: 0);
}
int main() { return f(3); }''',
    # _BitInt switch
    '''int f(unsigned _BitInt(7) x) {
    switch (x) {
    case (unsigned _BitInt(7))0: return 1;
    case (unsigned _BitInt(7))127: return 2;
    default: return 3;
    }
}
int main() { return f(3); }''',
    # statement expr with _BitInt
    '''long f(long v) {
    unsigned _BitInt(9) b = (unsigned _BitInt(9))v;
    return ({ unsigned _BitInt(9) t = b << 2; t == (b & (unsigned _BitInt(9))-4); });
}
int main() { return f(5); }''',
    # VLA of _BitInt
    '''void f(int n) {
    unsigned _BitInt(13) arr[n];
    for (int i = 0; i < n; i++) arr[i] = (unsigned _BitInt(13))i;
}
int main() { f(4); }''',
    # compound literal _BitInt
    '''long f(long x) {
    return *(unsigned _BitInt(11)[]){ (unsigned _BitInt(11))x };
}
int main() { return f(5); }''',
    # _Generic selecting _BitInt type then arithmetic
    '''#define promote(x) _Generic((x), unsigned _BitInt(5): (unsigned _BitInt(10))(x), default: (x))
long f(long v) {
    unsigned _BitInt(5) b = (unsigned _BitInt(5))v;
    return (long)(promote(b) << 1);
}
int main() { return f(5); }''',
    # _BitInt bit-field in struct
    '''struct S { unsigned _BitInt(7) x : 5; unsigned _BitInt(9) y : 7; };
int f(struct S s) {
    return (int)(s.x + s.y);
}
int main() { struct S s = {3, 4}; return f(s); }''',
    # ternary on _BitInt with int
    '''long f(unsigned _BitInt(6) a, int b) {
    return (long)(a > 3 ? a : b);
}
int main() { return f(5, 7); }''',
    # __builtin_overflow with _BitInt
    '''int f(unsigned _BitInt(9) a) {
    unsigned _BitInt(9) r;
    return __builtin_add_overflow(a, (unsigned _BitInt(9))100, &r) ? (int)r : -1;
}
int main() { return f(3); }''',
    # array subscript _BitInt
    '''int arr[64];
int f(unsigned _BitInt(6) i) {
    return arr[i];
}
int main() { return f(3); }''',
    # _BitInt function pointer
    '''typedef unsigned _BitInt(9) (*fp_t)(unsigned _BitInt(9));
unsigned _BitInt(9) g(unsigned _BitInt(9) x) { return x + 1; }
long f() {
    fp_t p = g;
    return (long)p(5);
}
int main() { return f(); }''',
    # _Atomic _BitInt
    '''#include <stdatomic.h>
_Atomic unsigned _BitInt(12) g;
long f() {
    atomic_store(&g, (unsigned _BitInt(12))7);
    return (long)atomic_load(&g);
}
int main() { return f(); }''',
]

FLAGS = [["-std=c23"], ["-std=c23", "-O2"], ["-std=c2x"], []]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t15_s{si}_f{fi}", "src": src, "tag": "clang",
                   "flags": fl, "ext": ".c"}
