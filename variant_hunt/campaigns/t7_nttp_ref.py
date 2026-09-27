"""Campaign t7: mutations of llvm/crash/test7.cpp
Seed: function-local static bound to reference NTTP -> segfault during
instantiation (constant-size-type info on dependent type).
Axes: NTTP kind/type, where the static lives, instantiation shape.
"""

SHAPES = [
    # original
    '''#include <iostream>
template<int& T>
void FuncTemplate() {{
    std::cout << "ref: " << T << std::endl;
}}

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
    # double reference NTTP
    '''template<double& T>
void FuncTemplate() {{ (void)T; }}

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static double InternalVar = 4.3;
    FuncTemplate<InternalVar>();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
    # no iostream, simpler
    '''template<int& T>
void FuncTemplate() {{ T += 1; }}

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
    # pointer NTTP instead of reference
    '''template<int* T>
void FuncTemplate() {{ *T += 1; }}

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static int InternalVar = 43;
    FuncTemplate<&InternalVar>();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
    # class template NTTP
    '''template<int& T>
struct Holder {{ int get() {{ return T; }} }};

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static int InternalVar = 43;
    Holder<InternalVar> h;
    (void)h.get();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
    # static inside class template member fn
    '''template<int& T>
void FuncTemplate() {{ (void)T; }}

template<int i> struct A {{
    void g() {{
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
    }}
}};

int main()
{{
  A<1> a;
  a.g();
}}''',
    # const ref NTTP
    '''template<const int& T>
void FuncTemplate() {{ (void)T; }}

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static const int InternalVar = 43;
    FuncTemplate<InternalVar>();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
    # struct ref NTTP
    '''struct S {{ int x; }};
template<S& T>
void FuncTemplate() {{ (void)T.x; }}

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static S InternalVar{{43}};
    FuncTemplate<InternalVar>();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
    # array ref NTTP
    '''template<int (&T)[3]>
void FuncTemplate() {{ (void)T[0]; }}

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static int InternalVar[3] = {{4,3,2}};
    FuncTemplate<InternalVar>();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
    # two local statics
    '''template<int& T, int& U>
void FuncTemplate() {{ (void)T; (void)U; }}

template<int i> class A {{}};
template<int i> void g(A<i> &) {{
    static int V1 = 43;
    static int V2 = 44;
    FuncTemplate<V1, V2>();
}}

int main()
{{
  A<1> a;
  g(a);
}}''',
]

FLAGS = [[], ["-std=c++20"], ["-O2"], ["-std=c++17", "-O1"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape.replace("{{", "{").replace("}}", "}") + "\n"
        for fi, fl in enumerate(FLAGS[:1] if si % 2 else FLAGS):
            yield {"name": f"t7_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
