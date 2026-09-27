"""Campaign t9: mutations of llvm/crash/test9.cpp
Seed: deduction guide on inner class template with parameter-pack outer ->
crash during deduction-guide instantiation.
Axes: pack position, guide form, ctor forms, usage.
"""

SHAPES = [
    # original
    '''template <typename... Args>
struct outer {{
    template <typename Type>
    struct inner {{
        inner(Args...) {{ }}
    }};

    inner(Args...) -> inner<int>;
}};

int main() {{
    outer();
}}''',
    # with args at use
    '''template <typename... Args>
struct outer {{
    template <typename Type>
    struct inner {{
        inner(Args...) {{ }}
    }};

    inner(Args...) -> inner<int>;
}};

int main() {{
    outer o(1, 2.0, 'c');
    (void)o;
}}''',
    # guide to dependent type
    '''template <typename... Args>
struct outer {{
    template <typename Type>
    struct inner {{
        inner(Args...) {{ }}
    }};

    inner(Args...) -> inner<decltype(sizeof...(Args))>;
}};

int main() {{
    outer();
}}''',
    # two packs
    '''template <typename... Args>
template <typename... BArgs>
struct outer_two;

template <typename... Args>
struct outer {{
    template <typename Type>
    struct inner {{
        inner(Args..., Type) {{ }}
    }};

    inner(Args..., int) -> inner<int>;
}};

int main() {{
    outer();
}}''',
    # inner with default arg
    '''template <typename... Args>
struct outer {{
    template <typename Type = long>
    struct inner {{
        inner(Args...) {{ }}
    }};

    inner(Args...) -> inner<int>;
}};

int main() {{
    outer();
}}''',
    # non-empty pack bound + alias use
    '''template <typename... Args>
struct outer {{
    template <typename Type>
    struct inner {{
        inner(Args...) {{ }}
    }};

    inner(Args...) -> inner<int>;
}};

using O = outer<int, double>;

int main() {{
    O();
}}''',
    # guide inside inner referencing pack via declval-less expr
    '''template <typename... Args>
struct outer {{
    template <typename Type>
    struct inner {{
        inner(Args...) {{ }}
        inner(Type, Args...) {{ }}
    }};

    inner(Args...) -> inner<int>;
    inner(int, Args...) -> inner<long>;
}};

int main() {{
    outer();
}}''',
    # nested inner-inner
    '''template <typename... Args>
struct outer {{
    template <typename Type>
    struct inner {{
        inner(Args...) {{ }}
        template <typename U>
        struct innermost {{
            innermost(U, Args...) {{ }}
        }};
        template <typename U>
        innermost(U, Args...) -> innermost<U>;
    }};

    inner(Args...) -> inner<int>;
}};

int main() {{
    outer();
}}''',
]

FLAGS = [[], ["-std=c++17"], ["-std=c++20"], ["-O2"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape.replace("{{", "{").replace("}}", "}") + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t9_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
