"""Campaign t4: mutations of gcc/crash/test4.cpp
Seed: nested local structs, inner DMI uses sizeof of function-local static
constexpr array -> ICE enclosing_instantiation_of cp/pt.cc:15184.
Axes: nesting depth, DMI expression, array type, allocation expr, template kind.
"""

ARRAYS = [
    ('static constexpr char string[] = "mew";', "sizeof(string)"),
    ('static constexpr int arr[3] = {1,2,3};', "sizeof(arr)"),
    ('static constexpr char string[] = "hello world";', "sizeof(string)"),
    ('static constexpr double d[2] = {0.5, 1.5};', "sizeof(d)"),
    ('constexpr char string[] = "mew";', "sizeof(string)"),       # non-static
    ('static constexpr unsigned arr[8] = {};', "sizeof(arr)"),
    ('static constexpr char string[] = "mew";', "sizeof(string) * 2"),
    ('static constexpr char string[] = "mew";', "alignof(char) + sizeof(string)"),
    ('static constexpr char string[] = "mew";', "sizeof(string[0])"),
]

STRUCTS = [
    # original: nested s2 with ptr DMI using new(sizeof)
    '''template<typename T>
void foo() {{
    {arr}
    struct s1_t {{
        struct s2_t {{
            int dummy {{ 0 }};
            char* ptr {{ static_cast<char*>(::operator new({expr}))}};
        }} s2;
    }} object;
}};
int main() {{ foo<void>(); }}''',
    # DMI is plain int = sizeof
    '''template<typename T>
void foo() {{
    {arr}
    struct s1_t {{
        struct s2_t {{
            int dummy {{ 0 }};
            unsigned long sz {{ {expr} }};
        }} s2;
    }} object;
}};
int main() {{ foo<void>(); }}''',
    # single nesting level
    '''template<typename T>
void foo() {{
    {arr}
    struct s1_t {{
        int dummy {{ 0 }};
        char* ptr {{ static_cast<char*>(::operator new({expr}))}};
    }} object;
}};
int main() {{ foo<void>(); }}''',
    # triple nesting
    '''template<typename T>
void foo() {{
    {arr}
    struct s1_t {{
        struct s2_t {{
            struct s3_t {{
                int dummy {{ 0 }};
                char* ptr {{ static_cast<char*>(::operator new({expr}))}};
            }} s3;
        }} s2;
    }} object;
}};
int main() {{ foo<void>(); }}''',
    # lambda DMI
    '''template<typename T>
void foo() {{
    {arr}
    struct s1_t {{
        struct s2_t {{
            int dummy {{ 0 }};
            unsigned long sz {{ []{{ return {expr}; }}() }};
        }} s2;
    }} object;
}};
int main() {{ foo<void>(); }}''',
    # member array sized by expr
    '''template<typename T>
void foo() {{
    {arr}
    struct s1_t {{
        struct s2_t {{
            int dummy {{ 0 }};
            char buf[{expr}];
        }} s2;
    }} object;
}};
int main() {{ foo<void>(); }}''',
    # class template instead of function template
    '''template<typename T>
struct wrap {{
    void foo() {{
        {arr}
        struct s1_t {{
            struct s2_t {{
                int dummy {{ 0 }};
                char* ptr {{ static_cast<char*>(::operator new({expr}))}};
            }} s2;
        }} object;
    }}
}};
int main() {{ wrap<int> w; w.foo(); }}''',
    # two DMIs
    '''template<typename T>
void foo() {{
    {arr}
    struct s1_t {{
        struct s2_t {{
            int dummy {{ 0 }};
            char* ptr {{ static_cast<char*>(::operator new({expr}))}};
            int extra {{ (int){expr} }};
        }} s2;
    }} object;
}};
int main() {{ foo<void>(); }}''',
]

OPTS = [["-O0"], ["-O2"]]

def generate():
    for si, shape in enumerate(STRUCTS):
        for ai, (arr, expr) in enumerate(ARRAYS):
            src = shape.format(arr=arr, expr=expr) + "\n"
            for o in OPTS[:1] if (si + ai) % 2 else OPTS:
                yield {"name": f"t4_s{si}_a{ai}_{o[0][1:]}",
                       "src": src, "tag": "gxx", "flags": o, "ext": ".cpp"}
