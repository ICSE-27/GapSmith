"""Campaign t13: Clang C++20 coroutine + template + local static / NTTP hybrids.
Coroutines are a crash-rich Clang area not covered by current seeds.
Compile-mode (crash) hunt.
"""

SHAPES = [
    # coroutine + local static in template fn
    '''#include <coroutine>
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
template<typename T>
task foo() {
    static int InternalVar = 43;
    co_return;
}
int main() { foo<int>(); }''',
    # coroutine + local static bound to ref NTTP inside lambda
    '''#include <coroutine>
template<int& T> void FuncTemplate() { (void)T; }
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
template<typename T>
task foo() {
    [](){ static int InternalVar = 43; FuncTemplate<InternalVar>(); }();
    co_return;
}
int main() { foo<int>(); }''',
    # coroutine + missing typename in promise
    '''#include <coroutine>
template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   struct promise_type {
     T2 x;
     Tester get_return_object() { return {}; }
     std::suspend_never initial_suspend() { return {}; }
     std::suspend_never final_suspend() noexcept { return {}; }
     void return_void() {}
     void unhandled_exception() {}
   };
};
template <class T>
Tester<T> foo() { co_return; }
int main() { foo<int>(); }''',
    # coroutine + deduction guide + pack
    '''#include <coroutine>
template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };
    inner(Args...) -> inner<int>;
};
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
task bar() {
    outer();
    co_return;
}
int main() { bar(); }''',
    # coroutine + constant wrapper co_await
    '''#include <coroutine>
template <auto V>
struct ConstantWrapper {
  static constexpr auto value = V;
  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {
    return {};
  }
};
struct Plus {
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }
};
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
task bar() {
    constexpr auto cwv = ConstantWrapper<Plus{}>{}(ConstantWrapper<42>{}, ConstantWrapper<17>{});
    co_return;
}
int main() { bar(); }''',
    # coroutine with co_await on dependent type
    '''#include <coroutine>
template <class T>
struct Tester {
   struct Inner { using T2 = int; };
};
template <class T>
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
template <class T>
task<T> foo() {
    typename Tester<T>::Inner::T2 v = 0;
    co_await std::suspend_never{};
    (void)v;
}
int main() { foo<int>(); }''',
    # nested coroutine calls in template
    '''#include <coroutine>
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
template<typename T>
task inner() { co_return; }
template<typename T>
task outer2() {
    static int InternalVar = 43;
    inner<T>();
    co_return;
}
int main() { outer2<int>(); }''',
    # coroutine + ref NTTP of promise-local static
    '''#include <coroutine>
template<int& T> int FuncTemplate() { return T; }
struct task {
  struct promise_type {
    task get_return_object() { return {}; }
    std::suspend_never initial_suspend() { return {}; }
    std::suspend_never final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() {}
  };
};
template<typename T>
task foo() {
    static int InternalVar = 43;
    int x = FuncTemplate<InternalVar>();
    (void)x;
    co_return;
}
int main() { foo<int>(); }''',
]

FLAGS = [["-std=c++20"], ["-std=c++20", "-O2"], ["-std=c++23"], ["-std=c++20", "-O0"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t13_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
