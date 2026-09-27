struct S { int x; long y; };
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
}
