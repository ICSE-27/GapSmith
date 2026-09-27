template<auto& T>
void FuncTemplate() { T += 1; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar = 43;
    FuncTemplate<InternalVar>();
}

int main() {
  A<1> a;
  g(a);
}
