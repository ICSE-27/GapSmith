"""Campaign t6b: wave-2 for llvm test6.cpp (missing typename, crash in
getTypeInfoImpl / undeduced auto). Try dependent types in more exotic positions:
decltype(auto), base classes, default args, template args, alias templates,
concepts/requires, operator declarations.
"""

SHAPES = [
    # alias template member
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   template <class U> using Alias = typename Inner::T2;
   static void test();
};

template <class T>
Tester<T>::Inner::T2 getInnerT2() { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = getInnerT2<T>();
}

template struct Tester<int>;''',
    # decltype(auto) return
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
auto getInnerT2() -> Tester<T>::Inner::T2 { return {}; }

template <class T>
void Tester<T>::test() {
   decltype(auto) _ = getInnerT2<T>();
}

template struct Tester<int>;''',
    # default argument
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
void take(Tester<T>::Inner::T2 = 0) { }

template <class T>
void Tester<T>::test() {
   take<T>();
}

template struct Tester<int>;''',
    # operator declaration
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
Tester<T>::Inner::T2 operator+(Tester<T>::Inner::T2 a, Tester<T>::Inner::T2 b) { return a + b; }

template <class T>
void Tester<T>::test() {
   Tester<T>::Inner::T2 a = 1, b = 2;
   auto _ = a + b;
}

template struct Tester<int>;''',
    # template template usage
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
struct Wrap { Tester<T>::Inner::T2 v; };

template <class T>
void Tester<T>::test() {
   Wrap<T> w; w.v = 0;
}

template struct Tester<int>;''',
    # friend declaration
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
Tester<T>::Inner::T2 helper();

template <class T>
struct Friend {
   friend Tester<T>::Inner::T2 helper<T>();
};

template <class T>
void Tester<T>::test() {
   Friend<T> f;
}

template struct Tester<int>;''',
    # noexcept with dependent type call
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
Tester<T>::Inner::T2 getInnerT2() noexcept(sizeof(Tester<T>::Inner::T2) > 0) { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = getInnerT2<T>();
}

template struct Tester<int>;''',
    # requires clause (C++20)
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
   requires (sizeof(Tester<T>::Inner::T2) > 0)
Tester<T>::Inner::T2 getInnerT2() { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = getInnerT2<T>();
}

template struct Tester<int>;''',
]

FLAGS = [["-std=c++20"], ["-std=c++17"], ["-std=c++20", "-O2"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t6b_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
