"""Campaign t4c: local-static-in-template ICE vein with NEW C++ features:
coroutines, template lambdas, variable templates, concepts/requires with
sizeof of local static, fold expressions, structured bindings.
"""

SHAPES = [
    # C++20 coroutine with local static + local struct DMI
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
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        } s2;
    } object;
    co_return;
}
int main() { foo<int>(); }''',
    # template lambda (C++20) with local static + nested struct
    '''int main() {
    auto lam = []<typename T>() {
        static constexpr char string[] = "mew";
        struct s1_t {
            struct s2_t {
                int dummy { 0 };
                char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
            } s2;
        } object;
    };
    lam.template operator()<int>();
}''',
    # variable template context
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            static constexpr unsigned long sz = sizeof(string);
        } s2;
    } object;
};
template<typename T>
constexpr int use = (foo<T>(), 0);
int main() { return use<int>; }''',
    # requires clause on local struct method
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
    # concept defined via local sizeof
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        template<typename U>
        concept C = (sizeof(string) > 1) && sizeof(U) > 0;
        struct s2_t {
            int dummy { 0 };
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # fold expression over local static array
    '''template<typename T>
void foo() {
    static constexpr int arr[3] = {1,2,3};
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new((0 + ... + sizeof(arr[0]))))};
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # sizeof of local static in noexcept of enclosing template fn
    '''template<typename T>
void foo() noexcept {
    static constexpr char string[] = "mew";
    auto inner = []() noexcept(sizeof(string) > 0) {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        } s2;
        (void)s2;
    };
    inner();
};
int main() { foo<void>(); }''',
    # explicit specialization-ish: two instantiations sharing static
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
template void foo<int>();
template void foo<long>();
int main() { foo<void>(); }''',
]

FLAGS = [["-O0"], ["-O2"], ["-std=c++20"], ["-std=c++20", "-O2"], ["-std=c++17"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            if "-std=c++17" in fl and ("co_return" in src or "concept " in src or "requires" in src or "template operator()" in src):
                continue
            yield {"name": f"t4c_s{si}_f{fi}", "src": src, "tag": "gxx",
                   "flags": fl, "ext": ".cpp"}
