template<double& T>
void FuncTemplate() { T += 0.5; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static double InternalVar = 4.3;
    FuncTemplate<InternalVar>();
}

int main() {
  A<1> a;
  g(a);
}
