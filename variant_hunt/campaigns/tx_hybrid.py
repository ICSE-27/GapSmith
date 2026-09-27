"""Campaign tx_hybrid: cross-seed hybridization of the 4 LLVM crash patterns.
Missing-typename (t6) x local-static-ref-NTTP (t7) x trailing-return-wrapper
(t8) x deduction-guide-pack (t9) -- combined to reach different code paths.
"""

SHAPES = [
    # deduction guide on inner class + missing typename alias
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        using Alias = Type;
        inner(Args...) { }
    };
    inner(Args...) -> inner<int>;
};
template <typename... Args>
outer<Args...>::inner<int>::Alias helper(outer<Args...> o) { return {}; }
int main() {
    outer();
}''',
    # local static ref NTTP + trailing return deduction
    '''template<int& T>
auto FuncTemplate() -> decltype(T + 0) { return T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    auto v = FuncTemplate<InternalVar>();
    (void)v;
}

int main() {
  A<1> a;
  g(a);
}''',
    # constant wrapper + deduction guide
    '''template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        ConstantWrapper<sizeof...(Args)> cw;
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}''',
    # missing typename inside deduction guide target
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   template <typename U> struct holder { holder(U) {} };
   holder(Tester<T>::Inner::T2) -> holder<Tester<T>::Inner::T2>;
};
Tester<int>::holder h(0);''',
    # local static ref NTTP inside deduction guide context
    '''template<int& T>
void FuncTemplate() { (void)T; }

template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) {
            static int InternalVar = 43;
            FuncTemplate<InternalVar>();
        }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}''',
    # trailing return wrapper + missing typename
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <auto V>
struct CW { static constexpr auto value = V; };

template <class T>
auto getIt() -> Tester<T>::Inner::T2 { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = CW<getIt<T>()>{};
}

template struct Tester<int>;''',
    # lambda local static NTTP + constant wrapper
    '''template <auto V>
struct CW { static constexpr auto value = V; };
template<int& T>
void FuncTemplate() { (void)T; }
template<int i> class A {};
template<int i> void g(A<i> &) {
    []()
    {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
        constexpr auto w = CW<42>{};
        (void)w;
    }();
}
int main() {
  A<1> a;
  g(a);
}''',
    # deduction guide with pack + trailing return
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        auto get() -> decltype(sizeof...(Args)) { return 0; }
    };
    inner(Args...) -> inner<decltype(sizeof...(Args))>;
};
int main() {
    outer();
}''',
]

FLAGS = [[], ["-std=c++17"], ["-std=c++20"], ["-std=c++20", "-pedantic-errors"], ["-O2"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"tx_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
