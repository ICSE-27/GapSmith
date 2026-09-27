"""Campaign t20: cross-transfer LLVM seed patterns -> GCC 14.3.0.
local-static ref NTTP, missing typename, constant wrapper, deduction guides,
_BitInt(3) rotate on gcc (run), SLP narrowing on gcc (run).
"""

CXX_COMPILE = [
    # missing typename on gcc
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
    # local static ref NTTP on gcc
    '''template<int& T>
void FuncTemplate() { (void)T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # lambda local static NTTP on gcc
    '''template<int& T>
void FuncTemplate() { (void)T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    []()
    {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
    }();
}

int main() {
  A<1> a;
  g(a);
}''',
    # constant wrapper on gcc
    '''template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
struct Times {
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) * static_cast<U&&>(u)) {
    return static_cast<T&&>(t) * static_cast<U&&>(u);
  }
};
constexpr auto cwv = ConstantWrapper<Times{}>{}(ConstantWrapper<42>{}, ConstantWrapper<17>{});''',
    # deduction guide decltype sizeof pack on gcc
    '''template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };
    inner(Args...) -> inner<decltype(sizeof...(Args))>;
};
int main() {
    outer();
}''',
]

RUN_C = [
    # _BitInt(3) rotate on gcc C23
    '''#include <stdio.h>
__attribute__((noinline))
long f(long x) {
  unsigned _BitInt(3) v = (unsigned _BitInt(3))(x >> 8);
  unsigned _BitInt(3) s = (unsigned _BitInt(3))(v << 2);
  unsigned _BitInt(3) m = (unsigned _BitInt(3))(v & (unsigned _BitInt(3))(-4));
  return s == m ? 1 : 3;
}
int main() {
  int exp[8] = {1,3,1,3,3,1,3,1};
  int bad = 0;
  for (long a = 0; a < 8; a++) {
    long r = f(a << 8);
    if (r != exp[a]) { printf("a=%ld got=%ld expected=%d\\n", a, r, exp[a]); bad++; }
  }
  printf(bad ? "RESULT: wrong\\n" : "RESULT: correct\\n");
  return bad;
}''',
    # wider widths on gcc
    '''#include <stdio.h>
#define W 13
typedef unsigned _BitInt(W) BT;
__attribute__((noinline))
long f(long x) {
  BT v = (BT)(x >> 8);
  BT s = (BT)(v << 2);
  BT m = (BT)(v & (BT)(-4));
  return s == m ? 1 : 3;
}
__attribute__((noinline))
long ref(long x) {
  volatile long xl = x;
  unsigned long long uv = ((unsigned long long)(xl >> 8)) & ((1ULL << W) - 1);
  unsigned long long us = (uv << 2) & ((1ULL << W) - 1);
  unsigned long long um = (uv & ((unsigned long long)(-4) & ((1ULL << W) - 1)));
  return (us == um) ? 1 : 3;
}
int main() {
  int bad = 0;
  for (long a = 0; a < (1L << W); a++) {
    long r = f(a << 8), e = ref(a << 8);
    if (r != e) { printf("a=%ld got=%ld exp=%ld\\n", a, r, e); bad++; }
  }
  printf(bad ? "RESULT: wrong %d\\n" : "RESULT: correct\\n", bad);
  return bad;
}''',
]

RUN_CXX = [
    # SLP narrowing on g++
    '''#include <stdio.h>
unsigned int acc = 0;
unsigned short a[6][6];
short b[6];

__attribute__((noinline)) void test() {
    for (long long i = 0; i < 6; i += 2)
        for (long long j = 0; j < 6; j += 2)
            acc += a[j][i] & (a[j][i] >= b[j]);
}

int main() {
    for (int i = 0; i < 6; i++) {
        b[i] = 14288;
        for (int j = 0; j < 6; j++) a[i][j] = 61035;
    }
    test();
    printf("acc=%u (expected 9)\\n", acc);
    return acc != 9;
}''',
    # stride-3 SLP on g++
    '''#include <stdio.h>
unsigned int acc = 0;
unsigned short a[6][6];
short b[6];

__attribute__((noinline)) void test() {
    for (long long i = 0; i < 6; i += 3)
        for (long long j = 0; j < 6; j += 1)
            acc += a[j][i] & (a[j][i] >= b[j]);
}

int main() {
    for (int i = 0; i < 6; i++) {
        b[i] = 14288;
        for (int j = 0; j < 6; j++) a[i][j] = 61035;
    }
    test();
    printf("acc=%u (expected 12)\\n", acc);
    return acc != 12;
}''',
]

def generate():
    i = 0
    for src in CXX_COMPILE:
        for fi, fl in enumerate([[], ["-std=c++20"], ["-O2"], ["-std=c++20", "-O2"]]):
            yield {"name": f"t20_x{i}_f{fi}", "src": src, "tag": "gxx",
                   "flags": fl, "ext": ".cpp"}
        i += 1
    i = 0
    for src in RUN_C:
        yield {"name": f"t20_c{i}", "src": src, "tag": "gcc",
               "flags": ["-std=c23"], "mode": "run",
               "optlevels": ["-O0", "-O1", "-O2", "-O3"], "ext": ".c"}
        i += 1
    i = 0
    for src in RUN_CXX:
        yield {"name": f"t20_s{i}", "src": src, "tag": "gxx",
               "flags": ["-std=c++11"], "mode": "run",
               "optlevels": ["-O0", "-O1", "-O2", "-O3"], "ext": ".cpp"}
        i += 1
