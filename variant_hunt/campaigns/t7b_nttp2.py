"""Campaign t7b: wave-2 for llvm test7.cpp (local static as reference NTTP).
Try: subobject references, NTTP of auto type, function-local statics in
different template contexts, template-template, constexpr contexts.
"""

SHAPES = [
    # auto NTTP (C++17)
    '''template<auto& T>
void FuncTemplate() { T += 1; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # member subobject ref NTTP
    '''struct S { int x; int y; };
template<int& T>
void FuncTemplate() { (void)T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static S InternalVar = {43, 44};
    FuncTemplate<InternalVar.x>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # static in lambda inside template
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
    # static local in constexpr function template
    '''template<int& T>
constexpr int FuncTemplate() { return T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    constexpr int v = FuncTemplate<InternalVar>();
    (void)v;
}

int main() {
  A<1> a;
  g(a);
}''',
    # NTTP ref bound to static in nested local struct
    '''template<int& T>
void FuncTemplate() { (void)T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    struct Local {
        static int get() {
            static int InternalVar = 43;
            FuncTemplate<InternalVar>();
            return InternalVar;
        }
    };
    Local::get();
}

int main() {
  A<1> a;
  g(a);
}''',
    # two-level instantiation
    '''template<int& T>
void FuncTemplate() { (void)T; }

template<int i> void inner() {
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}

template<int i> class A {};
template<int i> void g(A<i> &) {
    inner<i>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # extern "C" static
    '''template<int& T>
void FuncTemplate() { (void)T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static long InternalVar = 43;
    FuncTemplate<(int&)InternalVar>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # reference NTTP used as template arg of another template
    '''template<int& T> struct RefHolder { static int get() { return T; } };
template<int& T>
void FuncTemplate() {
    RefHolder<T> h; (void)h.get();
}

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}

int main() {
  A<1> a;
  g(a);
}''',
]

FLAGS = [[], ["-std=c++17"], ["-std=c++20"], ["-O2"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t7b_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
