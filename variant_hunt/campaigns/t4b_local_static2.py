"""Campaign t4b: wave-2 for gcc test4.cpp (enclosing_instantiation_of ICE).
Broader: sizeof/alignof of local statics in DMIs at various nesting depths,
requires-clauses, concepts, lambdas, decltype, member templates.
"""

SHAPES = [
    # requires clause referencing local static sizeof
    '''#include <type_traits>
template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
            static constexpr unsigned long sz = sizeof(string);
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # decltype in DMI
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            decltype(sizeof(string)) sz { sizeof(string) };
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # noexcept spec with sizeof
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        } s2;
        void method() noexcept(sizeof(string) > 0) {}
    } object;
};
int main() { foo<void>(); }''',
    # enum with sizeof value
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            enum { SZ = (int)sizeof(string) };
            int dummy { SZ };
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # static_assert in local struct
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            static_assert(sizeof(string) > 1, "");
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # template member struct
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        template<typename U>
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        };
        s2_t<int> s2;
    } object;
};
int main() { foo<void>(); }''',
    # generic lambda DMI
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { [](auto v){ return static_cast<char*>(::operator new(v)); }(sizeof(string)) };
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # static constexpr inside member fn of local struct
    '''template<typename T>
void foo() {
    struct s1_t {
        struct s2_t {
            static constexpr char string[] = "mew";
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # class template enclosing, dependent sizeof
    '''template<typename T>
struct wrap {
    void foo() {
        static constexpr T arr[4] = {};
        struct s1_t {
            struct s2_t {
                int dummy { 0 };
                char* ptr { static_cast<char*>(::operator new(sizeof(arr)))};
            } s2;
        } object;
    }
};
int main() { wrap<int> w; w.foo(); }''',
    # non-type template param from sizeof
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char buf[sizeof(string)];
            char* ptr { buf };
        } s2;
    } object;
    (void)sizeof(object);
};
int main() { foo<void>(); }''',
]

OPTS = [["-O0"], ["-O2"], ["-std=c++20"], ["-std=c++17"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for oi, o in enumerate(OPTS):
            yield {"name": f"t4b_s{si}_o{oi}", "src": src, "tag": "gxx",
                   "flags": o, "ext": ".cpp"}
