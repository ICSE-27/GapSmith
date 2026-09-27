"""Campaign t6: mutations of llvm/crash/test6.cpp
Seed: missing typename on dependent nested alias as return type -> crash in
getTypeInfoImpl (undeduced auto) on Clang 19.1.0, asserts-off.
Axes: use context of the dependent type, nesting shape, instantiation style.
"""

SHAPES = [
    # original: return type
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
   static void test();
}};

template <class T>
/*typename*/ Tester<T>::Inner::T2 getInnerT2() {{ return {{}}; }}

template <class T>
void Tester<T>::test() {{
   auto _ = getInnerT2<T>();
}}

template struct Tester<int>;''',
    # param type
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
   static void test();
}};

template <class T>
void takeInnerT2(Tester<T>::Inner::T2) {{ }}

template <class T>
void Tester<T>::test() {{
   takeInnerT2<T>(0);
}}

template struct Tester<int>;''',
    # local variable declaration
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
   static void test();
}};

template <class T>
void Tester<T>::test() {{
   Tester<T>::Inner::T2 v = 0;
   (void)v;
}}

template struct Tester<int>;''',
    # member variable
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
   struct Holder {{
      Tester<T>::Inner::T2 m;
   }};
   static void test();
}};

template <class T>
void Tester<T>::test() {{
   Holder h; h.m = 0;
}}

template struct Tester<int>;''',
    # static member function returning it, deeper nesting
    '''template <class T>
struct Tester {{
   struct Inner {{
      struct Innermost {{
         using T3 = long;
      }};
   }};
   static void test();
}};

template <class T>
Tester<T>::Inner::Innermost::T3 getT3() {{ return {{}}; }}

template <class T>
void Tester<T>::test() {{
   auto _ = getT3<T>();
}}

template struct Tester<int>;''',
    # function template called from main (implicit inst)
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
}};

template <class T>
Tester<T>::Inner::T2 getInnerT2() {{ return {{}}; }}

int main() {{
   auto x = getInnerT2<int>();
   (void)x;
}}''',
    # dependent alias of alias
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
   using Alias = Inner::T2;
   static void test();
}};

template <class T>
Tester<T>::Alias getA() {{ return {{}}; }}

template <class T>
void Tester<T>::test() {{
   auto _ = getA<T>();
}}

template struct Tester<int>;''',
    # noexcept / decltype context
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
   static void test();
}};

template <class T>
auto getInnerT2() -> Tester<T>::Inner::T2 {{ return {{}}; }}

template <class T>
void Tester<T>::test() {{
   auto _ = getInnerT2<T>();
}}

template struct Tester<int>;''',
    # cast expression
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
   static void test();
}};

template <class T>
void Tester<T>::test() {{
   auto _ = static_cast<Tester<T>::Inner::T2>(1.5);
   (void)_;
}}

template struct Tester<int>;''',
    # sizeof context
    '''template <class T>
struct Tester {{
   struct Inner {{
      using T2 = int;
   }};
   static void test();
}};

template <class T>
void Tester<T>::test() {{
   constexpr unsigned long s = sizeof(Tester<T>::Inner::T2);
   (void)s;
}}

template struct Tester<int>;''',
]

FLAGS = [["-std=c++20"], ["-std=c++17"], ["-std=c++20", "-O2"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape.replace("{{", "{").replace("}}", "}") + "\n"
        for fi, fl in enumerate(FLAGS[:1] if si % 2 else FLAGS):
            yield {"name": f"t6_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
