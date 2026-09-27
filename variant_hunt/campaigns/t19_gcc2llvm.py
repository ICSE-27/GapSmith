"""Campaign t19: cross-transfer GCC seed patterns -> Clang 19.1.0.
_Float16 ternary / excess precision, constexpr member-ptr conversions,
local-static sizeof DMI in nested local structs, nested-fn analog via blocks.
Crash hunt on clang/clang++.
"""

C_SHAPES = [
    # _Float16 ternary on clang (GCC ICE analog)
    '''typedef _Float16 FT;
FT f(FT x, FT m) {
    return (x < m) ? !(m + 1) : (x * m);
}''',
    '''typedef _Float16 FT;
int main() {
    FT x = (FT)3.14, y = (FT)1.0, m = (FT)0.5;
    return (int)((x < y) ? !(m + 1) : (x * y));
}''',
    # _Float16 ternary with int logical-not (gcc 5720 shape)
    '''typedef _Float16 TFtype;
int main() {
    TFtype x = (TFtype)3.14;
    TFtype y = (TFtype)1.0;
    int n = 0;
    return (y == x) ? (int)(y + n) : !(x - y);
}''',
    # _Float16 complex ternary
    '''typedef _Float16 FT;
FT f(FT x, _Complex FT c) {
    return (x > 0) ? !((FT)__real__ c) : x;
}''',
    # bf16 ternary
    '''typedef __bf16 FT;
FT f(FT x, FT m) {
    return (x < m) ? !(m + 1) : (x * m);
}''',
    # nested-fn analog: C blocks capturing
    '''void outer() {
    __attribute__((unused)) void (^g)() = ^{};
    g();
    void (^h)() = ^{};
    h();
}''',
]

CXX_SHAPES = [
    # constexpr member ptr across virtual inheritance on clang
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : virtual Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
template <typename T=int> void generate() {
  constexpr help h{static_cast<fn_t>(&Derived::doit)};
}
void f() { generate(); }''',
    # constexpr union member ptr
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
union help {
  fn_t ptr;
  unsigned long raw;
  constexpr help(fn_t p) : ptr(p) {}
};
template <typename T=int> void generate() {
  constexpr help h(static_cast<fn_t>(&Derived::doit));
}
void f() { generate(); }''',
    # local static sizeof DMI nested structs on clang
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # requires-clause mangle analog on clang
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            void method() requires (sizeof(string) > 1) {}
        } s2;
    } object;
    object.s2.method();
};
int main() { foo<void>(); }''',
    # decltype sizeof DMI on clang
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            decltype(sizeof(string)) sz { sizeof(string) };
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # asm goto +m outputs on clang (expected correct)
    '''int test(int trigger_abort) {
    int saved = -1;
    int flag = trigger_abort ? 0 : 1;
    asm volatile goto (
        "  movl $0, %%eax\\n\\t"
        "  movl %%eax, %[saved]\\n\\t"
        "  movl %[flag], %%eax\\n\\t"
        "  testl %%eax, %%eax\\n\\t"
        "  je %l[abort_lbl]\\n\\t"
        : [saved]"+m"(saved), [flag]"+m"(flag)
        :
        : "eax", "memory"
        : abort_lbl
    );
    if (flag == 0) __builtin_abort();
    return saved + 1;
abort_lbl:
    return saved - 1;
}
int main() { return test(0) + test(1); }''',
]

def generate():
    i = 0
    for src in C_SHAPES:
        for fi, fl in enumerate([[], ["-O1"], ["-O2"], ["-std=c23"]]):
            yield {"name": f"t19_c{i}_f{fi}", "src": src, "tag": "clang",
                   "flags": fl, "ext": ".c"}
        i += 1
    i = 0
    for src in CXX_SHAPES:
        for fi, fl in enumerate([[], ["-std=c++20"], ["-O2"], ["-std=c++20", "-O2"]]):
            yield {"name": f"t19_x{i}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
        i += 1
