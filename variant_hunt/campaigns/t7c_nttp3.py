"""Campaign t7c: NTTP NEW axes for Clang: floating-point NTTP, class-type NTTP
with captures, subobject reference NTTP, address-of-array-element, local static
in consteval/constexpr templates, NTTP used in more instantiation contexts.
"""

SHAPES = [
    # double NTTP bound to local static double
    '''template<double& T>
void FuncTemplate() { T += 0.5; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static double InternalVar = 4.3;
    FuncTemplate<InternalVar>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # subobject of local static struct (member ref NTTP)
    '''struct S { int x; long y; };
template<long& T>
void FuncTemplate() { (void)T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static S InternalVar = {1, 43};
    FuncTemplate<InternalVar.y>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # array element address as pointer NTTP
    '''template<int* T>
void FuncTemplate() { (void)(*T); }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalArr[4] = {1,2,3,4};
    FuncTemplate<&InternalArr[2]>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # consteval function template with local static NTTP
    '''template<int& T>
consteval int getVal() { return T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    constexpr int v = getVal<InternalVar>();
    (void)v;
}

int main() {
  A<1> a;
  g(a);
}''',
    # NTTP ref in variable template instantiation
    '''template<int& T>
int VarTemplate = T + 1;

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    (void)VarTemplate<InternalVar>;
}

int main() {
  A<1> a;
  g(a);
}''',
    # lambda static + class-type NTTP chain
    '''struct Wrap { int v; };
template<const Wrap& T>
void FuncTemplate() { (void)T.v; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    []()
    {
        static Wrap InternalVar = {43};
        FuncTemplate<InternalVar>();
    }();
}

int main() {
  A<1> a;
  g(a);
}''',
    # ref NTTP in nested template-template
    '''template<int& T>
struct Holder {
    template<int& U>
    struct Inner { int get() { return T + U; } };
    template<int& U>
    void use() { Inner<U> i; (void)i.get(); }
};

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int V1 = 43;
    static int V2 = 44;
    Holder<V1> h;
    h.use<V2>();
}

int main() {
  A<1> a;
  g(a);
}''',
    # local static in constexpr if branch
    '''template<int& T>
void FuncTemplate() { (void)T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    if constexpr (i > 0) {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
    }
}

int main() {
  A<1> a;
  g(a);
}''',
]

FLAGS = [[], ["-std=c++17"], ["-std=c++20"], ["-O2"], ["-std=c++23"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            if fl and fl[0] in ("-std=c++17",) and ("consteval" in src or "if constexpr" in src):
                pass  # if constexpr ok in 17; consteval not
            yield {"name": f"t7c_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
