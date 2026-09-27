struct S { int x; };
template<S& T>
void FuncTemplate() { (void)T.x; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static S InternalVar{43};
    FuncTemplate<InternalVar>();
}

int main()
{
  A<1> a;
  g(a);
}
