template<int& T>
auto FuncTemplate() -> decltype(T + 0) { return T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    auto v = FuncTemplate<InternalVar>();
    (void)v;
}

int main() {
  A<1> a;
  g(a);
}
