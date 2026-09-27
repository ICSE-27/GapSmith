struct S { int x; int y; };
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
}
