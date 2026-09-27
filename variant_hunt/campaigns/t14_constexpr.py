"""Campaign t14: constexpr/consteval chains in Clang templates — constexpr
virtual calls, constexpr dynamic_cast, constexpr placement new, static constexpr
local in template + requires, consteval propagation with wrappers. Crash hunt.
"""

SHAPES = [
    # constexpr virtual call in template
    '''struct Base { virtual constexpr int f() const { return 1; } };
struct Derived : Base { constexpr int f() const override { return 2; } };
template<typename T>
constexpr int foo() {
    static constexpr Derived d{};
    constexpr Base& b = d;
    return b.f();
}
constexpr int v = foo<int>();
int main() { return v - 2; }''',
    # constexpr dynamic_cast
    '''struct Base { virtual ~Base() = default; int x = 1; };
struct Derived : Base { int y = 2; };
template<typename T>
constexpr int foo() {
    static constexpr Derived d{};
    constexpr const Base* b = &d;
    constexpr const Derived* p = dynamic_cast<const Derived*>(b);
    return p ? p->y : 0;
}
constexpr int v = foo<int>();
int main() { return v - 2; }''',
    # local static constexpr + requires on outer template
    '''template <typename T>
struct Tester {
   static void test();
};

template <typename T>
   requires (sizeof(T) >= 0)
void Tester<T>::test() {
   static constexpr char string[] = "mew";
   struct Local {
       int dummy { 0 };
       char* ptr { static_cast<char*>(::operator new(sizeof(string))) };
   } object;
   (void)object;
}

template struct Tester<int>;''',
    # consteval function returning wrapper
    '''template <auto V>
struct CW { static constexpr auto value = V; };
template <class T>
consteval auto make() { return CW<sizeof(T)>{}; }
template <class T>
constexpr auto get() { return make<T>(); }
constexpr auto v = get<int>();
int main() { return (int)decltype(v)::value - 4; }''',
    # constexpr placement new in template
    '''#include <new>
template<typename T>
constexpr int foo() {
    alignas(T) static char buf[sizeof(T)];
    constexpr int unused = 0;
    T* p = new (buf) T();
    return (void)p, unused;
}
constexpr int v = foo<int>();
int main() { return v; }''',
    # requires on lambda inside template
    '''template<typename T>
void foo() {
    auto lam = [](auto x) requires (sizeof(x) >= sizeof(int)) { return x + 1; };
    static constexpr char string[] = "mew";
    (void)lam((int)sizeof(string));
}
int main() { foo<void>(); }''',
    # consteval + local static + NTTP
    '''template<int& T>
consteval int getRef() { return T; }
template<int i>
void g() {
    static int InternalVar = 43;
    if consteval {
        (void)0;
    } else {
        (void)0;
    }
    constexpr int v = 0;
    (void)v;
}
int main() { g<1>(); }''',
    # constexpr reference member binding
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   struct Holder {
      const Tester<T>::Inner::T2& r;
   };
   static void test();
};

template <class T>
void Tester<T>::test() {
   static constexpr typename Inner::T2 val = 5;
   Holder h{val};
   (void)h.r;
}

template struct Tester<int>;''',
]

FLAGS = [["-std=c++20"], ["-std=c++20", "-O2"], ["-std=c++23"], ["-std=c++17"], []]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            if fl and fl[0] == "-std=c++17" and ("consteval" in src or "requires" in src or "concept" in src):
                continue
            yield {"name": f"t14_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
