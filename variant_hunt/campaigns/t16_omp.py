"""Campaign t16: OpenMP compile-crash hunt (clang -fopenmp). Valid-ish OpenMP
constructs combined with templates, lambdas, nested functions-in-templates.
Compile-mode only (crash/error).
"""

SHAPES = [
    # omp parallel for in template
    '''template<typename T>
void foo(T *a, int n) {
    #pragma omp parallel for
    for (int i = 0; i < n; i++) a[i] = a[i] + 1;
}
template void foo<int>(int*, int);''',
    # omp with lambda body
    '''void foo(int *a, int n) {
    auto lam = [&](int i) { a[i] *= 2; };
    #pragma omp parallel for
    for (int i = 0; i < n; i++) lam(i);
}
template void foo<int>(int*, int);''',
    # omp target teams with template
    '''template<typename T>
void foo(T *a, int n) {
    #pragma omp target teams distribute parallel for map(tofrom: a[0:n])
    for (int i = 0; i < n; i++) a[i] = a[i] + 1;
}
template void foo<int>(int*, int);''',
    # omp simd reduction with dependent type
    '''template <class T>
struct Tester {
   struct Inner { using T2 = int; };
   static T2 foo(T2 *a, int n) {
       T2 s = 0;
       #pragma omp simd reduction(+:s)
       for (int i = 0; i < n; i++) s += a[i];
       return s;
   }
};
template struct Tester<int>;''',
    # omp task with local static NTTP
    '''template<int& T> void FuncTemplate() { (void)T; }
template<int i>
void g() {
    #pragma omp task
    {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
    }
}
int main() { g<1>(); }''',
    # omp declare reduction on template type
    '''template<typename T>
struct P { T v; };
#pragma omp declare reduction(+: P<int>: omp_out.v += omp_in.v)
template<typename T>
T foo(P<T> *a, int n) {
    P<T> s{0};
    #pragma omp parallel for reduction(+:s)
    for (int i = 0; i < n; i++) s.v += a[i].v;
    return s.v;
}
template int foo<int>(P<int>*, int);''',
    # omp parallel with nested template lambda
    '''template<typename T>
void foo(T *a, int n) {
    #pragma omp parallel
    {
        auto lam = []<typename U>(U x) { return x * 2; };
        #pragma omp for
        for (int i = 0; i < n; i++) a[i] = lam(a[i]);
    }
}
template void foo<int>(int*, int);''',
    # omp sections + structured binding
    '''void foo(int *a, int n) {
    #pragma omp parallel sections
    {
        #pragma omp section
        { auto [x, y] = *(int(*)[2])a; a[0] = x + y; }
        #pragma omp section
        { a[1] = a[0] * 2; }
    }
}''',
]

FLAGS = [["-fopenmp", "-O1"], ["-fopenmp"], ["-fopenmp", "-O2"], ["-fopenmp-simd", "-O2"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t16_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
