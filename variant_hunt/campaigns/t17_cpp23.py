"""Campaign t17: C++23 corners in Clang 19: deducing this, static operator(),
multidim subscript, if consteval — combined with the template/NTTP/local-static
veins from the seeds. Compile-mode crash hunt.
"""

SHAPES = [
    # deducing this + local static NTTP
    '''template<int& T> void FuncTemplate() { (void)T; }
struct S {
    template<typename Self>
    void f(this Self&& self) {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
    }
};
int main() { S s; s.f(); }''',
    # deducing this recursive
    '''template<int& T> void FuncTemplate() { (void)T; }
struct S {
    template<typename Self>
    void f(this Self&& self, int n) {
        if (n <= 0) {
            static int InternalVar = 43;
            FuncTemplate<InternalVar>();
            return;
        }
        self.f(n - 1);
    }
};
int main() { S s; s.f(1); }''',
    # static operator() lambda + dependent alias return
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
void Tester<T>::test() {
   auto lam = [](T x) static { return x; };
   auto _ = lam(T{});
}

template struct Tester<int>;''',
    # multidim subscript in template
    '''template<int& T> void FuncTemplate() { (void)T; }
struct M {
    template<typename... I>
    int operator[](I... i) {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
        return 0;
    }
};
int main() { M m; m[1, 2]; }''',
    # if consteval with wrapper instantiation
    '''template <auto V>
struct CW { static constexpr auto value = V; };
template <class T>
constexpr int foo() {
    if consteval {
        constexpr auto w = CW<sizeof(T)>{};
        return (int)decltype(w)::value;
    } else {
        return 0;
    }
}
constexpr int v = foo<int>();
int main() { return v - 4; }''',
    # deducing this + missing typename
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   template<typename Self>
   auto get(this Self&& self) -> Tester<T>::Inner::T2 { return {}; }
   static void test();
};

template <class T>
void Tester<T>::test() {
   Tester<T> t;
   auto _ = t.get();
}

template struct Tester<int>;''',
    # deduction guide + deducing this
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        template<typename Self>
        void f(this Self&&) { }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}''',
    # static lambda + deduction guide + pack
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };
    inner(Args...) -> inner<int>;
};
template <typename... Args>
void bar() {
    auto lam = [] static { outer<>(); };
    lam();
}
int main() { bar<int>(); }''',
]

FLAGS = [["-std=c++23"], ["-std=c++23", "-O2"], ["-std=c++2c"], ["-std=c++23", "-O0"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t17_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
