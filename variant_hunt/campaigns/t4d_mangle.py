"""Campaign t4d: mine the NEW mangle.cc:2264 signature vein.
Winner shape: requires-clause on a member fn of a nested local struct inside a
template, referencing sizeof of function-local static constexpr array.
Axes: requires/noexcept placement, member fn kinds (ctor/operator/static),
different local-entity references, deeper nesting, called/not-called.
"""

SHAPES = [
    # winner (requires on method, sizeof string)
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
    # requires on method, not called
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            void method() requires (sizeof(string) > 1) {}
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # requires on constructor
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            s2_t() requires (sizeof(string) > 1) {}
        } s2;
    } object;
};
int main() { foo<void>(); }''',
    # noexcept(sizeof)
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            void method() noexcept(sizeof(string) > 1) {}
        } s2;
    } object;
    object.s2.method();
};
int main() { foo<void>(); }''',
    # requires referencing the static directly (not sizeof)
    '''template<typename T>
void foo() {
    static constexpr int arr[3] = {1,2,3};
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            void method() requires (arr[0] == 1) {}
        } s2;
    } object;
    object.s2.method();
};
int main() { foo<void>(); }''',
    # requires on operator()
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            int operator()(int x) requires (sizeof(string) > 1) { return x; }
        } s2;
    } object;
    (void)object.s2(1);
};
int main() { foo<void>(); }''',
    # single-level local struct with requires method
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        int dummy { 0 };
        void method() requires (sizeof(string) > 1) {}
    } object;
    object.method();
};
int main() { foo<void>(); }''',
    # static member function with requires
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            static void smethod() requires (sizeof(string) > 1) {}
        } s2;
    } object;
    decltype(object)::s2_t::smethod();
};
int main() { foo<void>(); }''',
    # trailing requires on template member
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            template<typename U> void method(U) requires (sizeof(string) > 1 && sizeof(U) > 0) {}
        } s2;
    } object;
    object.s2.method(0);
};
int main() { foo<void>(); }''',
    # requires referencing alignof of local static
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            void method() requires (alignof(string) >= 1) {}
        } s2;
    } object;
    object.s2.method();
};
int main() { foo<void>(); }''',
    # requires referencing decltype of local static
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            void method() requires (sizeof(decltype(string)) > 1) {}
        } s2;
    } object;
    object.s2.method();
};
int main() { foo<void>(); }''',
    # friend function with requires inside local struct
    '''template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            friend void helper(s2_t) requires (sizeof(string) > 1) {}
        } s2;
    } object;
    helper(object.s2);
};
int main() { foo<void>(); }''',
]

FLAGS = [["-std=c++20"], ["-std=c++20", "-O2"], ["-std=c++23"], ["-std=c++20", "-O0"],
         ["-std=c++20", "-fno-inline"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t4d_s{si}_f{fi}", "src": src, "tag": "gxx",
                   "flags": fl, "ext": ".cpp"}
