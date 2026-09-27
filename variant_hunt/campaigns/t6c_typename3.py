"""Campaign t6c: missing-typename/dependent-type crash vein, NEW positions:
concepts, requires-clauses, explicit instantiation decl/def mismatch,
partial specialization, friend, decltype(auto), alias of alias chains,
default member init with dependent type.
"""

SHAPES = [
    # requires clause using dependent nested alias
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
concept HasT2 = requires { typename Tester<T>::Inner::T2; };

template <class T>
   requires HasT2<T>
Tester<T>::Inner::T2 getIt() { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = getIt<T>();
}

template struct Tester<int>;''',
    # default member initializer of dependent type
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   struct Holder {
      Tester<T>::Inner::T2 m = 5;
   };
   static void test();
};

template <class T>
void Tester<T>::test() {
   Holder h;
   (void)h.m;
}

template struct Tester<int>;''',
    # friend function declaration with dependent return
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
   friend Tester<T>::Inner::T2 helper(Tester<T>&) { return {}; }
};

template <class T>
void Tester<T>::test() {
   Tester<T> t;
   auto _ = helper(t);
}

template struct Tester<int>;''',
    # explicit instantiation declaration then use
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
};

template <class T>
Tester<T>::Inner::T2 getIt();

extern template int getIt<int>();

template <class T>
Tester<T>::Inner::T2 getIt() { return {}; }

template int getIt<int>();''',
    # partial specialization missing typename
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
};

template <class T, class U>
struct Wrap { U v; };

template <class T>
struct Wrap<T, Tester<T>::Inner::T2> { Tester<T>::Inner::T2 v; };

Wrap<int, int> w;''',
    # alias of alias chain
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   using A1 = Inner::T2;
   using A2 = A1;
   static void test();
};

template <class T>
Tester<T>::A2 getIt() { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = getIt<T>();
}

template struct Tester<int>;''',
    # decltype(auto) var of dependent type
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
void Tester<T>::test() {
   Tester<T>::Inner::T2 v = 0;
   decltype(auto) r = (v);
   (void)r;
}

template struct Tester<int>;''',
    # dependent type in exception spec + return
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static void test();
};

template <class T>
auto getIt() noexcept(false) -> Tester<T>::Inner::T2 { return {}; }

template <class T>
void Tester<T>::test() {
   auto _ = getIt<T>();
}

template struct Tester<int>;''',
]

FLAGS = [["-std=c++20"], ["-std=c++17"], ["-std=c++20", "-O2"], []]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t6c_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
