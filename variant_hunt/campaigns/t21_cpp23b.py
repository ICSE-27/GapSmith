"""Campaign t21: more C++23/C++20 clang FE combos — static operator() with NTTP,
subobject NTTP in deducing-this, if consteval + local static, template
multidim subscript chains, static lambda + missing typename.
"""

SHAPES = [
    # static lambda with local static NTTP
    '''template<int& T> void FuncTemplate() { (void)T; }
template<int i> void g() {
    []()
    {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
    }();
}
int main() { g<1>(); }''',
    # static lambda + multidim subscript + NTTP
    '''template<int& T> void FuncTemplate() { (void)T; }
struct M {
    template<typename... I>
    auto operator[](I... i) static {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
        return 0;
    }
};
int main() { M::operator[](1, 2); }''',
    # deducing this + subobject NTTP
    '''template<int& T> void FuncTemplate() { (void)T; }
struct S { int a; int b; };
struct W {
    template<typename Self>
    void f(this Self&& self) {
        static S InternalVar = {1, 43};
        FuncTemplate<InternalVar.b>();
    }
};
int main() { W w; w.f(); }''',
    # if consteval + local static NTTP
    '''template<int& T> consteval int ceval() { return T; }
template<int i> void g() {
    if consteval {
        static int InternalVar = 43;
        constexpr int v = ceval<InternalVar>();
        (void)v;
    }
}
int main() { g<1>(); }''',
    # static operator() in class + missing typename
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static Tester<T>::Inner::T2 op() { return {}; }
   static void test() {
       auto _ = Tester<T>::op();
   }
};
template struct Tester<int>;''',
    # template multidim subscript with pack + deduction
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        template<typename... I>
        Type operator[](I...) { return {}; }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}''',
    # multidim subscript returning dependent type
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   struct M {
       template<typename... I>
       Tester<T>::Inner::T2 operator[](I...) { return {}; }
   };
   static void test() {
       M m; auto _ = m[1, 2];
   }
};
template struct Tester<int>;''',
    # lambda in template default arg
    '''template<int& T> void FuncTemplate() { (void)T; }
template<int i>
void g(int x = []()
    {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
        return 0;
    }()) {
    (void)x;
}
int main() { g<1>(); }''',
]

FLAGS = [["-std=c++23"], ["-std=c++23", "-O2"], ["-std=c++20"], ["-std=c++26"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t21_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
